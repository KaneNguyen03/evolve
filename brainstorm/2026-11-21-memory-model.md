# 2026-11-21 · Memory model

**Question:** how does Evolve manage memory? (README open question 2; kickoff idea #2, 🌱 seed.)

**Constraints already set by RFCs:**
- RFC 0003: fitness includes timing (`latency_ms`, `p99_ms`), and a gene whose incumbent scores vary beyond their confidence interval is rejected as **flaky**. Memory management that adds timing noise makes evolution harder.
- RFC 0004: variants run in a sandbox with **memory budgets**; safety machinery fails closed.
- RFC 0005: arrays and DataFrames share **Arrow buffers**, which are immutable and reference-counted, with zero-copy moves into frames.
- RFC 0001: "if a Python programmer can guess what a line does, keep it." No mandatory lifetime annotations.

---

## Options (conservative → radical)

### A. Reference counting + cycle collector (the CPython model)
```evo
node.next = node                     # a cycle; the cycle collector reclaims it later
```
- **Benefits:** every persona; use case 2 (agents and humans reason about it the way they reason about Python).
- **Success measure:** Python programs port with zero memory annotations; deterministic destruction (files close at scope end).
- **Fails / abused:** cycle-collection pauses add timing noise; atomic counts are slow across threads. Guardrail: sandbox **memory budgets** cap leaks from evolved code that builds cycles.

### B. Tracing generational GC (Julia, Go, JVM)
```evo
cache = {}                           # no counts; a background collector traces reachable objects
```
- **Benefits:** use cases 4, 12 (throughput on allocation-heavy numeric and model code).
- **Success measure:** allocation throughput vs. Julia on a shared benchmark.
- **Fails / abused:** pause times make `latency_ms` fitness noisy, which trips RFC 0003's flaky-fitness rule; destruction timing is nondeterministic. Guardrail: **budgets** bound heap size, but nothing fixes the noise.

### C. Precise RC with reuse analysis (Perceus-style, as in Koka and Lean 4)
```evo
xs = xs |> map(_ + 1)                # updated in place when xs has a single owner, no copy
```
- **Benefits:** use cases 1, 4, 12 (data and tensor pipelines get in-place speed with Python-style code); use case 7 (predictable timing on edge devices).
- **Success measure:** allocations per pipeline step vs. A; p99 latency variance across 10 identical runs (target: inside RFC 0003's CI).
- **Fails / abused:** cycles still need a backstop collector; compiler complexity. Non-atomic counts for thread-local objects, atomic only for shared ones (Lean 4's approach), keep parallel populations fast. Guardrail: the memory manager is **`@conserved` runtime code**; no operator can mutate it.

### D. Mutable value semantics with copy-on-write (Swift structs, Hylo)
```evo
b = a; b[0] = 9                      # a is unchanged: b copied on first write
```
- **Benefits:** use cases 1, 4, 13 (no aliasing surprises in arrays, frames, prompts); use case 14 (agents can't share mutable state by accident).
- **Success measure:** zero aliasing bugs in the conformance corpus; copies avoided by uniqueness checks (needs C's counts).
- **Fails / abused:** differs from Python, where `b = a` aliases lists. Surprising for Python users. Guardrail: **invariants** in fitness catch behavior changes when a variant relies on aliasing.

### E. Inferred ownership with an optional `inout` escape hatch (Rust-lite, as in Mojo or Vale)
```evo
def push(xs: inout list[int], x: int): xs.append(x)
```
- **Benefits:** use cases 7, 12 (performance-critical kernels without a collector).
- **Success measure:** share of hot-path code that needs annotations (target: under 5%).
- **Fails / abused:** inference failures surface as confusing errors; it creeps toward Rust's learning curve. Guardrail: none needed at runtime (compile-time only), but it raises the barrier for agents writing code (use case 2).

### F. Arenas per evaluation (evolution-native)
```evo
with arena():                        # the runner wraps every fitness evaluation like this
    result = variant(example)        # everything allocated here is freed at once afterwards
```
- **Benefits:** use cases 1, 2, 5, 12: thousands of variant evaluations without leaks or GC work between them; each evaluation's memory use is measured exactly.
- **Success measure:** memory after N evaluations stays flat; evaluation memory reported per variant in the fitness report.
- **Fails / abused:** a value escaping the arena (stored in a global) must be detected and copied out, or rejected. Guardrail: **sandbox isolation** plus **fail closed**: escapes are an error, not a dangling pointer.

### G. Evolvable memory policy (memory tuning as a gene)
```evo
@evolve(strategy=mutate.parametric)  # tunes thresholds, arena sizes, collection triggers per workload
gene runtime_policy: MemoryPolicy
```
- **Benefits:** use cases 5, 7, 12 (workload-specific tuning without hand tweaking).
- **Success measure:** throughput and p99 after tuning vs. defaults on recorded workloads.
- **Fails / abused:** a policy that trades correctness for speed. Guardrail: only **parameters** evolve; the collector algorithm stays **`@conserved`**; promotion is **human-gated**.

### H. Pure immutability with persistent data structures (Clojure-style)
```evo
ys = xs.append(4)                    # returns a new list; xs is never modified
```
- **Benefits:** use case 14 (safe sharing between agents).
- **Fails:** `xs.append(4)` doing nothing to `xs` breaks every Python intuition; hidden structural sharing obscures costs.

---

## Converge

| Opt | Value | Feasibility (phase) | Safety risk | Status |
|---|---|---|---|---|
| A | Medium: familiar, simple | Phase 1 (interpreter) | Low | 🌿 growing: the Phase 1 subset of C |
| B | Medium: fast allocation | Phase 4 | Medium: noisy fitness | 🦴 fossil: pause noise conflicts with RFC 0003's flaky-fitness rule |
| C | **High**: Python ergonomics, in-place speed, predictable timing | Phase 4 (JIT), A first | Low | ⭐ 🌿 growing: **recommended** |
| D | Medium–high: no aliasing bugs | Phase 2–4, needs C's counts | Low | 🌿 growing: copy-on-write for arrays and frames only, Python aliasing for lists |
| E | Medium: kernels without GC | Post-1.0 | Low | 🌱 seed: revisit if C can't reach the performance target |
| F | **High**: evolution-specific, cheap, measurable | Phase 3 (fitness runner) | Low | ⭐ 🌿 growing: **recommended** |
| G | Medium | Phase 4+ | Medium | 🌱 seed: needs C and F first |
| H | Low | n/a | Low | 🦴 fossil: conflicts with Zen "Readable is better than clever" (hidden copying) and RFC 0001's Python-intuition rule |

**Recommendation:**
1. **C, starting as A.** Ship plain RC plus a cycle collector in the Phase 1 interpreter, designed so the Phase 4 JIT can add precise counting and reuse without changing program behavior. It's the only option that keeps Python semantics *and* predictable timing for latency fitness.
2. **F, independently.** Every fitness evaluation runs in its own arena. It makes thousands of evaluations cheap and leak-free and gives exact per-variant memory numbers, whatever the base memory model.

**Open follow-ups:**
- D's split (copy-on-write for arrays and frames, aliasing for lists and dicts) needs a teaching story. Is the rule "data types are values, containers are references" clear enough?
- How do arenas (F) interact with the WASM sandbox's linear memory? Possibly one WASM instance per evaluation already *is* the arena.
- Cycle collector placement in C: run between requests, or only on budget pressure, so it never lands inside a timed fitness call?
