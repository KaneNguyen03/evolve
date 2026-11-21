---
rfc: 0004
title: Promotion and safety model
status: draft
authors: [peace-program-project]
created: 2026-11-21
phase: Branch → Bloom
requires: [0002, 0003]
spec: []
---

# RFC 0004: Promotion and safety model

## Summary

Defines the **variant lifecycle**, **promotion gates**, **capabilities**, **`@conserved` code**, **budgets**, the **audit trail**, and the **threat model** for self-modifying Evolve programs. The core rule: **variants may be created freely in a sandbox; nothing reaches production without passing a gate.**

## Motivation

Self-modifying code is only acceptable if it's safer than a human editing code by hand: more tested, more traceable, and easier to undo. Every mission (AI models, AI-native apps, agent societies) depends on this RFC.

## Guide-level explanation

```evo
@conserved                                   # never mutated by any operator
def charge(card: Card, amount: Money) -> Receipt: ...

@capabilities(none)                          # pure: no I/O inside the sandbox or in prod
@heal(strategies=[mutate.structural, ask_agent], budget=budget(gens=20, cpu=10 min, usd=2), approve="human")
gene def parse_amount(raw: str) -> Money: ...
```

```bash
evo promote --list                         # candidates waiting for approval
evo promote billing.parse_amount@gen-8     # shows diff, fitness report, Lessons fixed, then asks
evo revert  billing.parse_amount@gen-7     # instant rollback, recorded as a lineage event
```

## Reference-level explanation

### Variant lifecycle

```
proposed ──▶ evaluated ──▶ candidate ──▶ approved ──▶ promoted ──▶ (superseded)
    │            │             │             │             │
    └────────────┴─────────────┴─────────────┴──▶ extinct ◀┘ (revert / invariant violation)
```

Every transition is a lineage event (RFC 0002) with an `actor`.

### Promotion gates

| Gate | Who approves | Allowed when |
|---|---|---|
| `human` (**default**) | A person with `promote` permission on the project | Always available |
| `tests` | The runner, automatically | Gene is `@capabilities(none)` (pure) **and** has at least one invariant **and** holdout size ≥ 50 |
| `auto` | The runner, automatically | Explicit opt-in per gene in `evo.toml` **and** `origin != prod`, or a `population` in shadow mode only |

A gate can only be relaxed in `evo.toml`, never in code that a mutation can touch. The `approve=` argument in source is a request that must match the config, or the runner refuses.

### Capabilities

- Default for any gene: **no capabilities**.
- Grantable: `fs.read(path)`, `fs.write(path)`, `net(host)`, `clock`, `random`, `env(name)`, `process`, `gpu`, `tool(name)` (AI tools), `sensor(name)`, `actuator(name)`.
- Capabilities are enforced at the **WASM sandbox boundary** (Phase 4) and by the interpreter's host functions before that.
- A variant can never request more capabilities than its incumbent. Widening capabilities is a human-only change to source and config.

### `@conserved`

- Applies to `def`, `module`, `schema`, `protocol`, and fields of `model`.
- No operator may produce a variant that changes conserved code or anything it transitively inlines.
- The runner hashes conserved items at the start of each run and refuses to promote if any hash changed.

### Budgets

Per heal or evolve run: generations, wall time, CPU time, memory, GPU hours, agent tokens, and money. Hitting a limit stops the run cleanly and records a `budget_exhausted` lineage event. Defaults are conservative (20 generations, 10 min CPU, $0 agent spend unless set).

### Audit trail

For every promotion, the record includes: diff against the incumbent, fitness report (visible and holdout, with CIs), invariants checked, Lessons resolved, operator and seed, for agentic operators the **full prompt and response**, and the approver. `evo audit <gene>` prints it.

### Threat model

| Threat | Example | Mitigation |
|---|---|---|
| Sandbox escape | A variant reads secrets from disk | WASM isolation, no ambient authority, capability checks |
| Gate bypass | A variant edits `approve="auto"` in its own source | Gates come from `evo.toml`; source `approve=` must match |
| Conserved tampering | A mutation changes `charge()` through inlining | Conserved hashes checked before promotion |
| Fitness gaming | A variant special-cases visible examples | Holdout, regression Lessons, size limits (RFC 0003) |
| Prompt injection via Lessons | A malicious input in a Lesson steers the agent operator | Redacted Lessons only, inputs as fingerprints by default, agent output treated as an untrusted proposal |
| Resource exhaustion | A variant loops forever | Budgets and per-call timeouts |
| Collusion (agent societies) | Agents jointly game a system fitness | Conserved protocols, per-agent invariants, human gates (future RFC) |

## Safety and failure modes

This RFC *is* the safety model. Failure of the safety machinery itself (sandbox crash, missing config) must **fail closed**: no promotion, a Lesson, and a clear error.

## Drawbacks

- Human gates slow down healing. That's intentional for v1; `tests` gates cover low-risk pure functions.
- Recording full agent prompts and responses costs storage and may contain sensitive Lesson content (already redacted).

## Alternatives

- **Signed variants** with external policy engines (OPA): possibly later, as an integration.
- **No auto gate at all:** simpler, but blocks useful offline evolution in dev and CI.

## Prior art

Capability-based security (WASI, Fuchsia, E language), deployment canaries and feature flags, code review requirements, supply-chain provenance (SLSA).

## Unresolved questions

1. Who holds `promote` permission in a project without a server (solo developer)? Proposal: the local git user, recorded by name.
2. Should promotion produce a git commit automatically, so lineage and git history stay aligned?
3. Minimum holdout size for the `tests` gate: is 50 right?

## Test plan

- Red-team test suite: one test per row of the threat model, each must fail closed.
- Gate tests: every combination of source `approve=` and `evo.toml` setting.
- Conserved-hash tests including inlined and transitively called code.
