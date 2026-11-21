# 🧪 EvoBench

A public benchmark of **real software failures caused by a changing environment**, and how well a system heals them. See the [roadmap](../docs/roadmap.md#4-evobench) for goals and targets.

## Case format v0

Each case is a folder in `cases/` named `NNNN-short-name`:

| File | Purpose |
|---|---|
| `case.toml` | Metadata: id, category, the gene a healer may change, environment change, fitness files, invariants |
| `program.py` | The program **as it was before** the environment changed. Phase 1 cases are Python; Evolve cases come later |
| `examples.jsonl` | **Visible** examples, one per line: `{"input": …, "expected": …}` or `{"input": …, "raises": "ErrorType"}` |
| `holdout.jsonl` | **Hidden** examples in the same format. Healers must never read this file |

Invariants in `case.toml` are Python expressions. A rule that mentions `result` is checked on every example's result. Any other rule is checked once, with the gene function and `date` in scope.

The scorer tells the two kinds apart by the word `result` anywhere in the rule, so keep that word out of a rule that is checked once, including inside its string literals.

## Scoring

```bash
python3 bench/run.py bench/cases/0001-date-format-drift                          # original program
python3 bench/run.py bench/cases/0001-date-format-drift --program candidate.py   # a healed candidate
```

A case is **healed** when the candidate passes every holdout row and violates no invariant (exit code 0).

## Rules for contributors

- 🔒 **Anonymize everything.** No personal data, secrets, customer names, or proprietary code.
- 🎯 Holdout must contain cases that a fix tailored only to the visible examples would get wrong.
- 🧱 At least one invariant that stops a "cheating" fix (for example, returning a constant).
- 📏 Keep programs small: one gene, under 50 lines.

## Checking a case

The rules above are easy to state and easy to miss, so a gate checks them:

```bash
python3 bench/check.py                                     # every case
python3 bench/check.py bench/cases/0001-date-format-drift  # one case
```

Each case has two reference programs in `checks/NNNN-short-name/`, kept outside the case folder so that folder stays exactly what a healer is given:

| File | What it is | The gate requires |
|---|---|---|
| `healed.py` | A correct fix | It heals the case and passes every visible example |
| `shortcut.py` | A plausible fix that only fits the visible examples | It passes every visible example and is **not** healed |

The gate also builds two programs of its own, a memorizer that is right only on the visible inputs and one that always returns a visible answer, and requires that neither is healed. It checks the original program too: it must fail in a way the examples show, and still pass some rows, so a fix that drops the old inputs is caught.

A case that passes can tell a real fix from the shortcut you thought of. It can't promise more than that, so choose the shortcut a hurried healer would write.

## Cases

| Id | Category | Difficulty | Summary |
|---|---|---|---|
| [0001](cases/0001-date-format-drift/) | format-drift | easy | Vendor switches order dates from ISO to day-first |
| [0002](cases/0002-customer-email-moved/) | schema-drift | easy | Orders API moves the customer's email into a nested object |
| [0003](cases/0003-not-found-becomes-error/) | api-contract | medium | Geocoding API v2 reports an unknown address as an error object |
| [0004](cases/0004-leap-day-renewal/) | edge-case | medium | Subscriptions that started on a leap day reach their first renewal |
