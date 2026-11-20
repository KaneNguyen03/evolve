<img src="../assets/logo/peace-mark.svg" width="72" align="right" alt="Peace logo"/>

# 🌿 Peace: Vision and Purpose

> **Peace is a programming language in which a program's failures make it better instead of only breaking it.**

---

## 1. The problem

Three trends are colliding:

1. **AI agents now write and repair a growing share of code**, but they work with almost no feedback loop. They read unstructured error text, guess a fix, check one bit ("did tests pass?"), and forget everything when the session ends.
2. **Software lives in environments that keep drifting.** Data schemas change, third-party APIs change, workloads change, and hardware changes. Code that was correct last month quietly becomes wrong. Fixing it is manual, reactive, and repetitive.
3. **Data and scientific work is still split across languages.** People prototype in Python, then rewrite hot paths in C, C++, or Rust (the "two-language problem"). Units, uncertainty, and data frames are bolted on as separate libraries that don't know about each other.

Each trend has partial answers: agent frameworks, AutoML, genetic-programming libraries, program-repair research, Julia. None of them makes **learning from failure** a property of the language itself.

## 2. The thesis

> Great languages turn a hard discipline into a primitive.
> Rust made *ownership* a primitive. Julia made *multiple dispatch and arrays* primitives.
> **Peace makes the improvement loop a primitive.**

The improvement loop is the oldest algorithm in nature:

```
observe failure → vary → measure → select → remember
```

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/diagrams/evolution-loop-dark.svg">
  <img alt="The Peace improvement loop: observe, vary, measure, select, remember" src="../assets/diagrams/evolution-loop-light.svg" width="720">
</picture>

In Peace, each step is a language construct:

| Step | Construct | Today, without Peace |
|---|---|---|
| Observe failure | `attempt / learn` → structured **Lesson** | Free-text stack traces in logs |
| Vary | `gene`, `mutate` | Hand edits or ad-hoc scripts |
| Measure | `fitness`, `invariant` | Separate test and benchmark tools; pass/fail only |
| Select | `population`, `select`, promotion gates | Code review and gut feeling |
| Remember | fossil record and lineage | Git log, if you're lucky |

Because the loop is part of the language, the compiler and runtime can make it **safe** (sandboxing, capabilities, conserved code), **cheap** (JIT, parallel populations), and **auditable** (lineage for every change).

## 3. Who Peace is for

| Persona | What they get |
|---|---|
| **AI agent builders** | A language whose errors, rewards, and memory are machine-readable by design, plus an MCP server to plug any agent in |
| **Data engineers** | Pipelines that survive schema drift and dirty input, with quarantine and partial results instead of 3 a.m. pages |
| **Researchers and scientists** | Python-like syntax, Julia-like speed, native units and uncertainty, and evolutionary search for models |
| **Platform engineers and SREs** | Integrations and heuristics that adapt to changing environments, behind explicit promotion gates |
| **Educators and learners** | A culture and toolchain where failure is visibly the first step of learning |

## 4. What makes Peace different

| Approach | Example | What it lacks that Peace adds |
|---|---|---|
| Evolutionary computation libraries | DEAP (Python) | Evolution lives *outside* the program; no sandbox, lineage, or production integration |
| Automated program repair research | GenProg | Research prototypes; repairs are one-off patches with no ongoing population or memory |
| LLM-driven algorithm discovery | FunSearch, AlphaEvolve (DeepMind) | Powerful but bespoke research systems; Peace aims to make this loop available to every developer |
| LM program optimizers | DSPy | Optimizes prompts and LM pipelines; Peace generalizes to any code, with typed invariants |
| Self-healing infrastructure | Kubernetes restarts, retries | Heals *processes*, not *logic*; a restart doesn't fix a wrong date parser |
| AI coding agents | Many | Strong at proposing edits, weak at measuring, remembering, and safely deploying them |
| Data-native languages | Julia | Excellent arrays and dispatch, but no failure-learning model and no Python-style syntax |

Peace isn't trying to beat any of these at its own game. Its bet is that **putting the loop, the data model, and the safety model in one language** unlocks things that gluing tools together can't.

## 5. Non-goals

To keep the project honest:

- **Peace is not "no humans needed".** Promotion to production is human-gated by default. Peace makes humans *faster* reviewers, not absent ones.
- **Peace is not AGI or magic.** Evolution only works where fitness can be measured. If you can't write a `fitness` block, Peace can't improve the code.
- **Peace does not replace Rust** for systems programming. It's built *on* Rust and calls into Rust crates freely.
- **Peace is not a genetic-programming toy.** Mutations must produce readable, reviewable source code, never opaque blobs.
- **Peace does not mutate everything.** Plain functions are plain. Evolution is opt-in per `gene`.

## 6. Design principles, in depth

1. **Failure is data.** Every failure has a schema: kind, inputs (redacted), context, environment, and stack. Lessons are values you can filter, group, and join.
2. **Imperfect and running beats perfect and absent.** Partial results, quarantine, and uncertainty (`±`) are first-class, so a program can keep delivering value while it heals.
3. **Readable evolution.** Mutations operate on a lossless syntax tree and render back to idiomatic source. A human must always be able to read the winning variant.
4. **Measured, not asserted.** "Better" means higher fitness on examples *and* holdouts, with every invariant intact.
5. **Safe by construction.** Variants run in a WASM sandbox with explicit capabilities and budgets. `@conserved` code is untouchable.
6. **Total recall.** Lineage records parent, diff, author (human, agent, or operator), fitness report, and approver for every promoted variant. Any ancestor can be restored.
7. **Data is native.** Arrays, broadcasting, data frames, units, and uncertainty are in the core, not in imports.
8. **Python-familiar, Julia-fast, Rust-solid.** Familiar syntax, specialized JIT code, and a memory-safe implementation.

## 7. What success looks like

By 1.0, we want to be able to say:

- A data pipeline written in Peace **heals most common real-world drift failures** without a code change from a human, beyond an approval click.
- An AI agent working in Peace **fixes more bugs, and repeats fewer mistakes**, than the same agent working in plain Python. We'll measure this on a public benchmark (see [PeaceBench](roadmap.md#4-peacebench)).
- Numeric Peace code runs **within a small constant factor of Julia**.
- **Zero** unapproved changes ever reach production by default.

See **[roadmap.md](roadmap.md)** for how we get there.
