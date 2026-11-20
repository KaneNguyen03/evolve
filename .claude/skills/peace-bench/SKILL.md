---
name: peace-bench
description: Author a PeaceBench case from a real-world failure, or heal and score a candidate fix against an existing case. Use for "add a PeaceBench case", "turn this bug into a bench case", "heal case 0001", or "score this fix on PeaceBench".
---

# PeaceBench

Format and rules: `bench/README.md`. Scorer: `python3 bench/run.py <case> [--program candidate.py]`.

## Author a case

1. Get the story: what worked, what changed in the environment, how it broke.
2. **Anonymize**: no personal data, secrets, customer names, or proprietary code. Rewrite as a small synthetic program with one gene, under 50 lines.
3. Create `bench/cases/NNNN-short-name/` with `case.toml`, `program.py`, `examples.jsonl`, `holdout.jsonl`.
4. Holdout must include rows that a fix tailored to the visible examples gets wrong. Add at least one invariant that defeats a cheating fix (such as returning a constant).
5. Check both directions:
   - `python3 bench/run.py <case>` on the original must exit **1**.
   - A reference fix, written in the scratchpad and not committed, must exit **0**.
6. Add the case to the table in `bench/README.md`.

## Heal a case (acting as the healer)

Read only `case.toml`, `program.py`, and `examples.jsonl`. **Never open `holdout.jsonl`**, because doing so invalidates the score. Write the candidate to the scratchpad, score it with `--program`, and report the examples, holdout, and invariant lines verbatim.
