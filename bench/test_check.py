"""Tests for the EvoBench case gate (bench/check.py).

    python3 -m unittest discover -s bench -p "test_*.py"

Each test builds a small bench tree in a temporary directory from case 0001 and
breaks one thing, then runs the gate the way a contributor would.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

BENCH = pathlib.Path(__file__).resolve().parent
CASE_ID = "0001-date-format-drift"


def check(*args):
    cmd = [sys.executable, str(BENCH / "check.py"), *map(str, args)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


class GateTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = pathlib.Path(tmp.name)
        self.case = root / "cases" / CASE_ID
        self.checks = root / "checks" / CASE_ID
        shutil.copytree(BENCH / "cases" / CASE_ID, self.case)
        shutil.copytree(BENCH / "checks" / CASE_ID, self.checks)

    def rewrite(self, path, old, new):
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def assert_fails(self, check_name):
        run = check(self.case)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn(f"  {check_name}:", run.stdout)
        return run

    def test_every_case_in_the_repo_passes(self):
        run = check()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn(f"{CASE_ID}  ok", run.stdout)

    def test_an_untouched_copy_passes(self):
        run = check(self.case)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_holdout_that_a_shortcut_passes_is_rejected(self):
        # Without the rows that must raise, the over-tolerant shortcut heals the case.
        holdout = self.case / "holdout.jsonl"
        kept = [line for line in holdout.read_text(encoding="utf-8").splitlines() if "raises" not in line]
        holdout.write_text("\n".join(kept) + "\n", encoding="utf-8")
        self.rewrite(self.case / "case.toml", 'rule = "2000 <= result.year <= 2100"', 'rule = "result.year >= 1"')
        self.assert_fails("shortcut")

    def test_holdout_that_repeats_visible_examples_is_rejected(self):
        examples = (self.case / "examples.jsonl").read_text(encoding="utf-8")
        (self.case / "holdout.jsonl").write_text(examples, encoding="utf-8")
        run = self.assert_fails("format")
        self.assertIn("also a visible example", run.stdout)

    def test_case_without_invariants_is_rejected(self):
        toml = self.case / "case.toml"
        text = toml.read_text(encoding="utf-8")
        toml.write_text(text[: text.index("[[invariants]]")], encoding="utf-8")
        run = self.assert_fails("format")
        self.assertIn("invariant", run.stdout)

    def test_reference_fix_that_does_not_heal_is_rejected(self):
        shutil.copy(self.case / "program.py", self.checks / "healed.py")
        self.assert_fails("healed")

    def test_program_that_already_passes_is_rejected(self):
        shutil.copy(self.checks / "healed.py", self.case / "program.py")
        self.assert_fails("original")

    def test_missing_reference_programs_are_reported(self):
        shutil.rmtree(self.checks)
        self.assert_fails("healed")


if __name__ == "__main__":
    unittest.main()
