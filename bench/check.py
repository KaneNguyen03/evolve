"""EvoBench case gate: can this case tell a real fix from a shortcut?

Usage:
    python3 bench/check.py                                     # every case in bench/cases
    python3 bench/check.py bench/cases/0001-date-format-drift  # one case

A case passes when all of these hold:

    format     case.toml, examples, and holdout follow format v0 and the rules for contributors
    original   the program is not healed, the failure is visible (an example fails too), and
               old inputs still work (it passes at least one example and one holdout row)
    healed     checks/<id>/healed.py, a correct fix, heals the case
    shortcut   checks/<id>/shortcut.py, a plausible but wrong fix, passes every visible
               example and is still not healed
    memorized  a program that is right only on the visible inputs is not healed
    constant   a program that always returns one of the visible answers is not healed

The reference programs live in bench/checks/, next to bench/cases/, so a case folder stays
exactly what a healer is given. Exit code 0 when every case passes, 1 otherwise.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import tomllib
from typing import NamedTuple

BENCH = pathlib.Path(__file__).resolve().parent
CATEGORIES = {"schema-drift", "format-drift", "api-contract", "edge-case", "dependency-upgrade", "performance-drift"}
DIFFICULTIES = {"easy", "medium", "hard"}
SOURCES = {"synthetic", "anonymized-real"}
MAX_PROGRAM_LINES = 50

LOADER = '''\
import importlib.util
import json


def _gene(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, {gene!r})


_healed = _gene({healed!r}, "evobench_healed")
'''

# Right on the visible inputs, unchanged everywhere else.
MEMORIZED = LOADER + '''\
_original = _gene({original!r}, "evobench_original")
_visible = set({visible!r})


def {gene}(value):
    known = json.dumps(value, sort_keys=True) in _visible
    return (_healed if known else _original)(value)
'''

# One correct visible answer, returned for every input.
CONSTANT = LOADER + '''\
_answer = _healed(json.loads({input!r}))


def {gene}(value):
    return _answer
'''


class Score(NamedTuple):
    healed: bool
    examples: tuple[int, int]
    holdout: tuple[int, int]
    scored: bool  # False when the scorer stopped before printing its counts


def score(case_dir, program=None):
    """Runs the reference scorer as a healer would and reads its report."""
    cmd = [sys.executable, str(BENCH / "run.py"), str(case_dir)]
    if program is not None:
        cmd += ["--program", str(program)]
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    counts = {
        name: (int(passed), int(total))
        for name, passed, total in re.findall(r"^(examples|holdout)\s+(\d+)/(\d+)$", run.stdout, re.MULTILINE)
    }
    return Score(run.returncode == 0, counts.get("examples", (0, 0)), counts.get("holdout", (0, 0)), len(counts) == 2)


def key(value):
    return json.dumps(value, sort_keys=True)


def read_rows(path, problems):
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(f"format: {path.name} line {number} is not JSON ({exc.msg})")
            continue
        if not isinstance(row, dict) or "input" not in row or ("expected" in row) == ("raises" in row):
            problems.append(f'format: {path.name} line {number} needs "input" and exactly one of "expected" or "raises"')
            continue
        rows.append(row)
    return rows


def check_format(case_dir, case, problems):
    """The parts of format v0 and the rules for contributors a machine can check."""
    fail = lambda message: problems.append(f"format: {message}")
    if not re.fullmatch(r"\d{4}-[a-z0-9]+(-[a-z0-9]+)*", case_dir.name):
        fail(f"the folder name must look like NNNN-short-name, not {case_dir.name!r}")
    if case.get("id") != case_dir.name:
        fail(f'id is {case.get("id")!r} but the folder is {case_dir.name!r}')
    for field, allowed in (("category", CATEGORIES), ("difficulty", DIFFICULTIES), ("source", SOURCES)):
        if case.get(field) not in allowed:
            fail(f"{field} is {case.get(field)!r}; use one of: {', '.join(sorted(allowed))}")
    if not case.get("environment_change", {}).get("summary", "").strip():
        fail("[environment_change] needs a summary of what changed")
    invariants = case.get("invariants", [])
    if not invariants:
        fail("add at least one invariant that a correct fix must never violate")
    for invariant in invariants:
        if not invariant.get("name") or not invariant.get("rule"):
            fail("every invariant needs a name and a rule")

    program, fitness = case.get("program", {}), case.get("fitness", {})
    missing = [f"[{table}] {field}" for table, field in
               (("program", "file"), ("program", "gene"), ("fitness", "examples"), ("fitness", "holdout"))
               if not case.get(table, {}).get(field)]
    if missing:
        fail(f"case.toml is missing {', '.join(missing)}")
        return None
    paths = {name: case_dir / value for name, value in
             (("program", program["file"]), ("examples", fitness["examples"]), ("holdout", fitness["holdout"]))}
    absent = [path.name for path in paths.values() if not path.is_file()]
    if absent:
        fail(f"missing file(s): {', '.join(absent)}")
        return None

    lines = paths["program"].read_text(encoding="utf-8").splitlines()
    if len(lines) > MAX_PROGRAM_LINES:
        fail(f"{paths['program'].name} has {len(lines)} lines; keep programs under {MAX_PROGRAM_LINES}")
    examples, holdout = read_rows(paths["examples"], problems), read_rows(paths["holdout"], problems)
    if not examples or not holdout:
        fail("examples and holdout each need at least one row")
    visible = {key(row["input"]) for row in examples}
    for row in holdout:
        if key(row["input"]) in visible:
            fail(f'holdout input {row["input"]!r} is also a visible example, so it is not hidden')
    return paths | {"example_rows": examples}


def check_case(case_dir):
    """Returns the list of problems with one case; empty means it passes."""
    problems = []
    try:
        case = tomllib.loads((case_dir / "case.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [f"format: can't read case.toml ({exc})"]
    files = check_format(case_dir, case, problems)
    if files is None:
        return problems
    gene = case["program"]["gene"]

    original = score(case_dir)
    if not original.scored:
        problems.append("original: the scorer stopped before reporting; run bench/run.py on the case to see why")
    else:
        if original.healed:
            problems.append("original: the program already passes, so there is nothing to heal")
        if original.examples[0] == original.examples[1]:
            problems.append("original: every visible example passes; show the failure in at least one example")
        if original.examples[0] == 0 or original.holdout[0] == 0:
            problems.append("original: add rows the program still gets right, in examples and in holdout, "
                            "so a fix that breaks the old inputs is caught")

    checks = case_dir.parent.parent / "checks" / case_dir.name
    healed_path, shortcut_path = checks / "healed.py", checks / "shortcut.py"
    if not healed_path.is_file():
        problems.append(f"healed: add {checks.name}/healed.py under bench/checks/, a correct fix; "
                        "without it nothing shows the case can be healed")
        return problems
    healed = score(case_dir, healed_path)
    if not healed.healed or healed.examples[0] != healed.examples[1]:
        problems.append(f"healed: healed.py does not heal the case "
                        f"(examples {healed.examples[0]}/{healed.examples[1]}, holdout {healed.holdout[0]}/{healed.holdout[1]})")
        return problems  # the generated programs below are built on healed.py

    if not shortcut_path.is_file():
        problems.append(f"shortcut: add {checks.name}/shortcut.py under bench/checks/, a plausible fix that only "
                        "fits the visible examples")
    else:
        shortcut = score(case_dir, shortcut_path)
        if shortcut.examples[0] != shortcut.examples[1]:
            problems.append(f"shortcut: shortcut.py fails a visible example "
                            f"({shortcut.examples[0]}/{shortcut.examples[1]}), so it is not a fix anyone would stop at")
        if shortcut.healed:
            problems.append("shortcut: shortcut.py is healed; add holdout rows or an invariant that catch it")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        names = {"gene": gene, "healed": str(healed_path), "original": str(files["program"])}
        rows = files["example_rows"]

        memorized = tmp / "memorized.py"
        memorized.write_text(MEMORIZED.format(visible=sorted(key(row["input"]) for row in rows), **names), encoding="utf-8")
        if score(case_dir, memorized).healed:
            problems.append("memorized: a program that is right only on the visible inputs is healed; "
                            "the holdout needs a failing input the examples don't show")

        answers = {}
        for row in rows:
            if "expected" in row:
                answers.setdefault(key(row["expected"]), row)
        for number, row in enumerate(answers.values()):
            constant = tmp / f"constant_{number}.py"
            constant.write_text(CONSTANT.format(input=json.dumps(row["input"]), **names), encoding="utf-8")
            if score(case_dir, constant).healed:
                problems.append(f'constant: a program that always returns {row["expected"]!r} is healed')
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", nargs="*", type=pathlib.Path, help="case folders (default: every case in bench/cases)")
    args = ap.parse_args()
    cases = args.cases or sorted(path for path in (BENCH / "cases").iterdir() if path.is_dir())

    failed = 0
    for case_dir in cases:
        problems = check_case(case_dir.resolve())
        print(f"{case_dir.name}  {'ok' if not problems else 'FAILED'}")
        for problem in problems:
            print(f"  {problem}")
        failed += bool(problems)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
