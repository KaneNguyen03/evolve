---
rfc: 0003
title: gene, fitness, and selection semantics
status: draft
authors: [peace-program-project]
created: 2026-11-21
phase: Sprout → Branch
requires: [0001, 0002]
spec: []
---

# RFC 0003: `gene`, `fitness`, and selection semantics

## Summary

Defines what a **gene** is, how **variants** are identified, how **fitness** is evaluated, and how the runtime **selects** a winner. Phase 1 implements this for parametric mutation in the Python engine. Phase 3 implements it natively in Peace with structural mutation.

## Motivation

"Better" has to be precise, reproducible, and hard to game, or evolution becomes a random-change generator. This RFC is the contract between mutation operators, the fitness runner, and the promotion pipeline (RFC 0004).

## Guide-level explanation

```peace
gene def evict_score(entry: CacheEntry, now: Time) -> float:
    alpha = ~1.0 in 0.5..=2.0                 # evolvable constant
    return entry.hits ^ alpha / (now - entry.last_access).seconds

fitness evict_score:
    benchmark replay"traces/2026-11.trace"
    holdout   replay"traces/2026-10.trace"
    score     = hit_rate - 0.1 * p99_latency_ms
    invariant result.is_finite()
```

```bash
peace evolve evict_score --generations 20 --seed 42
# gen  best   Δ vs incumbent  holdout  invariants  status
#   0  0.812  —               0.809    ✅          incumbent
#  14  0.851  +0.039 ± 0.006  0.846    ✅          candidate → awaiting approval
```

## Reference-level explanation

### Genes and variants

- A **gene** is a function declared with `gene def` (Peace) or `@gene` (Python engine). Its identity is its **fully qualified name** (`billing.parse_price`). The signature is the gene's **contract**: every variant must keep the same parameter names, types, and return type. Changing the contract is a new gene, not a variant.
- A **variant** is one implementation of a gene. Its id is `<gene>@gen-<n>` for promoted lines, plus a content hash: `billing.parse_price@gen-7#3f9a1c`.
- A variant record holds: `gene`, `generation`, `parents` (1 for mutation, 2 for recombination, 0 for the original), `source` (canonical CST text), `source_hash`, `params` (values of `~` constants), `operator` (which mutation produced it), `author` (`human:`, `agent:`, `operator:`), `created_at`.
- The **incumbent** is the currently promoted variant. Calls to a gene always dispatch to the incumbent unless a `population` routes some traffic elsewhere (shadow or canary).

### Evolvable constants

`~expr in range [scale]` declares a parameter the parametric operator may change. Scale hints: `lin` (default), `log`, `int`. A gene with no `~` constants can still evolve through structural or agentic operators.

### Fitness evaluation

A `fitness` block has four kinds of clauses:

| Clause | Role | Rule |
|---|---|---|
| `examples` / `benchmark` / `simulate` / `replay` | **Training signal** visible to operators and agents | At least one required |
| `holdout` | **Hidden** evaluation set | Never shown to operators or agents; if absent, the runner splits off 20% of examples by seeded hash |
| `score = expr` | Scalar to **maximize** | Evaluated over the whole set; may use built-in metrics (`accuracy`, `latency_ms`, `p99_ms`, `cost`, …) |
| `invariant expr` | **Hard constraint** | Checked on every evaluated call; one violation disqualifies the variant |

Evaluation of one variant:

1. Run in the sandbox (RFC 0004) with the gene's capabilities and the run budget.
2. Any exception counts as a failed example (and becomes a `sandbox` Lesson), unless the example expects that exception.
3. Compute `score` on visible data and on holdout, with a **bootstrap 95% confidence interval** (1,000 resamples, seeded).
4. Check all invariants. A violation sets `status = extinct` immediately, with the violating input fingerprint recorded.

### Selection

A variant becomes a **candidate** for promotion only if all of these hold:

1. All invariants pass on visible **and** holdout data.
2. Its holdout score beats the incumbent's by at least the gene's **margin** `δ` (default `0.01` of the score's range or `0.0` for pass-rate scores), and the lower bound of the CI of the difference is above zero.
3. It passes every **regression Lesson**: every past Lesson for this gene that has a `resolution` becomes a test case that must keep passing.
4. Its size is within limits (structural variants: at most 2× the incumbent's CST node count, to stop bloat).

Among candidates, the runner proposes the one with the best holdout score, ties broken by smaller source.

### Mutation operator interface

Every operator (built-in, Rust plugin, or agent) implements:

```
propose(gene, incumbent, lessons, fitness_spec_without_holdout, rng, budget) -> [Variant]
```

Operators **never** see holdout data and **never** write to the fossil record directly. The runner does.

### Determinism

Every evolution run records `seed`, operator versions, and, for agentic operators, the full prompt and response (RFC 0004). Re-running with the same seed and cached agent responses must reproduce the same variants and scores.

## Safety and failure modes

- **Goodhart's law:** holdout separation, regression Lessons, CI-based margins, and size limits all exist to stop variants from gaming visible examples.
- **Flaky fitness:** if the incumbent's own score varies by more than its CI across two runs, the runner refuses to select and reports the gene's fitness as flaky.
- **Contract drift:** a variant that changes the signature is rejected at proposal time.

## Drawbacks

- Bootstrap CIs and holdouts make evaluation several times more expensive than a single pass.
- Fixed `δ` defaults won't suit every score scale. Genes may need to set it explicitly.

## Alternatives

- **Pareto selection** over multiple objectives instead of a single `score`: more expressive, harder to explain. Could be added later as `score = pareto(a, b)`.
- **Bandit-style online selection** in production: powerful, but promotion without a gate conflicts with RFC 0004. Shadow populations cover the safe part.

## Prior art

Genetic programming (Koza), automated program repair (GenProg), population-based training, FunSearch and AlphaEvolve (LLM-proposed programs scored by evaluators), A/B testing statistics.

## Unresolved questions

1. Default `δ`: relative to what, when a score has no natural range?
2. Should recombination require both parents to be candidates, or just non-extinct?
3. How are examples weighted when Lessons add new cases continuously (recency weighting)?

## Test plan

- A toy gene with a known optimum: parametric evolution must reach it within N generations for fixed seeds.
- A gene with a deliberately leaky visible set: selection must refuse variants that overfit (holdout check).
- Determinism test: same seed, same cached agent responses, identical lineage.
