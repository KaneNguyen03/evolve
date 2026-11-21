"""Tests for the EvoBench reference scorer.

    python3 -m unittest discover -s bench -p "test_*.py"

The scorer's contract is its exit code (0 = healed), so each test runs it the way a
healer would: as a subprocess, with a candidate program on disk.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

BENCH = pathlib.Path(__file__).resolve().parent
CASE = BENCH / "cases" / "0001-date-format-drift"

HEALED = """
    import datetime

    def parse_order_date(raw):
        raw = raw.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.datetime.strptime(raw, fmt).date()
            except ValueError:
                pass
        raise ValueError(raw)
"""


def score(candidate=None, extra_invariant=None):
    """Runs the scorer on case 0001, optionally with `candidate` as the program source
    and with one more invariant rule added to a copy of the case."""
    with tempfile.TemporaryDirectory() as tmp:
        case = CASE
        if extra_invariant is not None:
            case = pathlib.Path(tmp) / CASE.name
            shutil.copytree(CASE, case)
            with open(case / "case.toml", "a", encoding="utf-8") as f:
                f.write(f"\n[[invariants]]\nname = \"extra\"\nrule = {extra_invariant!r}\n")
        cmd = [sys.executable, str(BENCH / "run.py"), str(case)]
        if candidate is not None:
            program = pathlib.Path(tmp) / "candidate.py"
            program.write_text(textwrap.dedent(candidate), encoding="utf-8")
            cmd += ["--program", str(program)]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


class ScorerTest(unittest.TestCase):
    def test_original_program_is_not_healed(self):
        run = score()
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIn("examples  2/5", run.stdout)
        self.assertIn("holdout   3/6", run.stdout)

    def test_healed_candidate_exits_zero(self):
        run = score(HEALED)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("holdout   6/6", run.stdout)
        self.assertIn("invariants ok", run.stdout)

    def test_constant_answer_is_not_healed(self):
        run = score("""
            import datetime

            def parse_order_date(raw):
                return datetime.date(2026, 11, 21)
        """)
        self.assertEqual(run.returncode, 1)

    def test_candidate_cannot_pick_the_exit_code_from_the_gene(self):
        run = score("""
            import sys

            def parse_order_date(raw):
                sys.exit(0)
        """)
        self.assertEqual(run.returncode, 1, "sys.exit(0) in the gene was scored as healed")
        self.assertIn("holdout   0/6", run.stdout)

    def test_candidate_cannot_pick_the_exit_code_at_import(self):
        run = score("""
            import sys

            sys.exit(0)
        """)
        self.assertEqual(run.returncode, 1, "sys.exit(0) at import was scored as healed")
        self.assertIn("failed to load", run.stdout)

    def test_candidate_that_fails_to_import_is_reported_without_a_traceback(self):
        run = score("def parse_order_date(raw) -> oops")
        self.assertEqual(run.returncode, 1)
        self.assertIn("failed to load", run.stdout)
        self.assertNotIn("Traceback", run.stderr)

    def test_invariant_that_raises_counts_as_violated(self):
        # Right text, wrong type: `result.year` raises AttributeError on a str.
        run = score(HEALED.replace(".date()", ".date().isoformat()"))
        self.assertEqual(run.returncode, 1)
        self.assertNotIn("Traceback", run.stderr)
        self.assertIn("invariants VIOLATED", run.stdout)
        self.assertIn("never-invent-dates on input", run.stdout)

    # A rule is checked on every result only when it reads the name `result`.

    def test_rule_with_the_word_result_in_a_string_is_checked_once(self):
        rule = "len('result') == 6 and parse_order_date('2026-11-21') == date(2026, 11, 21)"
        run = score(HEALED, extra_invariant=rule)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("invariants ok", run.stdout)

    def test_rule_with_result_inside_a_longer_name_is_checked_once(self):
        rule = "[results for results in [parse_order_date('2026-11-21')]] == [date(2026, 11, 21)]"
        run = score(HEALED, extra_invariant=rule)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_rule_that_reads_result_is_still_checked_on_every_row(self):
        run = score(HEALED, extra_invariant="result.year != 2024")
        self.assertEqual(run.returncode, 1)
        self.assertIn("extra on input '2024-02-29'", run.stdout)
        self.assertIn("extra on input '29/02/2024'", run.stdout)


if __name__ == "__main__":
    unittest.main()
