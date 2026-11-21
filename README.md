<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner/evolve-banner-dark.svg">
  <img alt="Evolve: programs that learn from failure. Python-readable, Julia data-native, Rust-built." src="assets/banner/evolve-banner-light.svg" width="100%">
</picture>

<br/>

[![Status: Seed](https://img.shields.io/badge/status-seed%20·%20design%20stage-000000?style=flat-square)](docs/roadmap.md)
[![Built with Rust beta](https://img.shields.io/badge/built%20with-Rust%20beta-000000?style=flat-square&logo=rust&logoColor=white)](rust-toolchain.toml)
[![Python-readable](https://img.shields.io/badge/syntax-Python--readable-000000?style=flat-square&logo=python&logoColor=white)](#-three-heritages)
[![Julia data-native](https://img.shields.io/badge/data-Julia--native-000000?style=flat-square&logo=julia&logoColor=white)](#-three-heritages)
[![PRs welcome](https://img.shields.io/badge/PRs%20%26%20RFCs-welcome-000000?style=flat-square)](CONTRIBUTING.md)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-000000?style=flat-square)](LICENSE)

**🧬 A programming language that evolves through failure.**<br/>
Programs that mutate, experiment, learn from their mistakes, and heal themselves.

[🌿 Vision](docs/vision.md) · [🧪 Use cases](docs/use-cases.md) · [🗺️ Roadmap](docs/roadmap.md) · [📜 RFCs](rfcs/README.md) · [🧪 EvoBench](bench/README.md) · [🎨 Brand](docs/brand.md) · [🤝 Contribute](CONTRIBUTING.md)

</div>

> [!NOTE]
> 🌱 **Evolve is in the Seed stage.** Nothing is implemented yet. This repository is where we work out *why* Evolve should exist and *what* people (and AI agents) will build with it. Ideas, critiques, and real-world failure stories are the most valuable contributions right now.

---

## 📚 Table of contents

| | | |
|---|---|---|
| 🎯 [Mission](#-mission) | 🌿 [Why Evolve?](#-why-evolve) | 🧘 [The Zen of Evolve](#-the-zen-of-evolve) |
| ✨ [A first taste](#-a-first-taste) | 🧬 [Three heritages](#-three-heritages) | 🦠 [The evolutionary model](#-the-evolutionary-model) |
| 🧠 [Evolve for AI](#-evolve-for-ai-models-apps-and-agent-systems) | 🛡️ [Safety guardrails](#️-safety-evolution-with-guardrails) | 🧪 [Use cases](#-use-cases) |
| 🦀 [Architecture](#-architecture-built-on-rust-beta) | 🧰 [Toolchain](#-toolchain-sketch) | 🗺️ [Roadmap](#️-roadmap) |
| ❓ [Open questions](#-open-questions) | 🤝 [Contributing](#-contributing) | 📄 [License](#-license) |

---

## 🎯 Mission

**Evolve exists to build the next generation of AI systems: systems that evolve, adapt, and stay safe while doing it.**

<table>
<tr>
<td width="33%" valign="top">

### 🧠 Next-generation AI models
Models that are **optimized, safe, and robust**, that **interact with the world**, and that **evolve and adapt to their context**. They're built from **modular** parts that can be swapped, specialized, and improved independently.

</td>
<td width="33%" valign="top">

### 📱 AI-native applications
Applications where prompts, tools, memory, and evaluations are **first-class language features**. Every failure becomes a Lesson the app learns from.

</td>
<td width="33%" valign="top">

### 🕸️ Agent-to-agent systems
Societies of agents that **communicate through typed, versioned protocols**, cooperate on goals, and **evolve as a system**, while the contracts between them stay conserved and safe.

</td>
</tr>
</table>

Underneath all three is the same foundation: 🍂 **failure as data**, 🧬 **evolution as a language feature**, and 🛡️ **safety by construction**.

---

## 🌿 Why Evolve?

> **Evolve is a programming language in which a program's failures make it better instead of only breaking it.**

Most programming languages treat failure as an enemy. An exception is something to be caught, silenced, or allowed to crash the program. Then a human reads a stack trace, guesses a fix, and redeploys. The program itself learns nothing.

Nature works differently. For about four billion years, life has improved through **variation, failure, and selection**. Most mutations fail. The failures aren't wasted: they're how the population learns what doesn't work. What survives is fit for its environment, and the history is recorded in the genome. 🧬

### 🔥 The problem

- 🤖 **AI agents write and repair more and more code**, yet they get unstructured error text, a pass/fail signal, and no memory across sessions.
- 🌊 **Software lives in drifting environments.** Schemas, APIs, and workloads change, and the same kinds of fixes are made by hand again and again.
- 🧩 **Data work is split across languages and libraries.** Python for prototyping, C or Rust for speed, and separate packages for frames, units, and uncertainty.

### 💡 The thesis

Rust made *ownership* a primitive. Julia made *dispatch and arrays* primitives. **Evolve makes the improvement loop a primitive.**

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/evolution-loop-dark.svg">
  <img alt="The Evolve improvement loop: 1 Observe (attempt/learn), 2 Vary (gene, mutate), 3 Measure (fitness, invariant), 4 Select (population, promote), 5 Remember (fossil record, lineage), around a sandboxed, budgeted, human-gated runtime." src="assets/diagrams/evolution-loop-light.svg" width="760">
</picture>
</div>

Because the loop lives in the language, Evolve can make it **🛡️ safe** (sandbox, capabilities, conserved code), **⚡ cheap** (JIT, parallel populations), and **🔍 auditable** (lineage for every change).

### 👥 Who it's for

| 🧠 AI model & agent builders | 🛠️ Data engineers | 🔬 Researchers | 🏗️ Platform engineers & SREs | 🎓 Educators |
|:---:|:---:|:---:|:---:|:---:|
| Modular models, typed agent protocols, safety invariants, and machine-readable feedback | Pipelines that survive drift | Speed, units, and uncertainty | Integrations that adapt | Failure as the first step of learning |

### 🚫 What Evolve is not

- ❌ **Not "no humans needed".** Production changes are human-gated by default.
- ❌ **Not magic.** No measurable fitness means no evolution.
- ❌ **Not a Rust replacement.** It's built *on* Rust.
- ❌ **Not a black box.** Every evolved variant is readable source code.

📖 Full rationale, prior art, and comparison with other approaches: **[docs/vision.md](docs/vision.md)**

---

## 🧘 The Zen of Evolve

*In the spirit of `import this`:*

```
Readable is better than clever.
Failure is data, not disaster.
Imperfect and running beats perfect and absent.
Every mutation has a lineage.
Survival is earned by fitness, not by assertion.
Mutate boldly in the sandbox; promote carefully to the world.
Conserve what must never change.
Uncertainty should be measured, not hidden.
Data is a first-class citizen, not an import.
A program that cannot learn is already extinct.
Humans hold the final say over what survives.
```

---

## ✨ A first taste

### 🐍 Looks like Python, on purpose

```evo
# hello.evo
def greet(name: str) -> str:
    return f"Hello, {name}. Welcome to Evolve."

print(greet("world"))
```

### 📊 Data is native (Julia heritage)

```evo
xs = [1.0, 2.0, 3.0, 4.0]
ys = sin.(xs) .+ 1                 # broadcast any function with `.`

A = rand(4, 4)
β = A \ ys                         # linear solve, built-in

sales = read"data/sales.parquet"   # DataFrame literal loader (Arrow-backed)
sales
  |> filter(_.region == "EU")
  |> groupby(:month)
  |> sum(:revenue)
```

### 📏 Imperfection is native

```evo
g     = 9.81 ± 0.02 m/s²           # values carry uncertainty and units
t     = 1.30 ± 0.05 s
drop  = 0.5 * g * t^2              # uncertainty propagates automatically
print(drop)                        # 8.29 ± 0.64 m
```

### 🍂 Failure is a teacher

```evo
attempt:
    config = load_toml("app.toml")
learn err:
    remember err                   # recorded as a structured Lesson in the fossil record
    config = Config.defaults()
```

`attempt / learn` behaves like `try / except`, with one difference: every failure becomes a **Lesson** (type, context, inputs, stack, environment) that people, the runtime, and AI agents can query later.

### 🩹 Code that evolves and heals

```evo
@heal(strategies=[retry, mutate, ask_agent], budget=20, approve="human")
gene def parse_price(raw: str) -> Money:
    return Money.parse(raw.strip(), currency="USD")

fitness parse_price:
    examples  "tests/prices.csv"                  # input → expected output
    score     = accuracy - 0.001 * latency_ms
    invariant result.amount >= 0                  # a mutation may never break this
```

- 🧬 `gene` marks a function as **evolvable**.
- 🎯 `fitness` defines what "better" means for it.
- 🩹 `@heal` says what to do when it fails in production: retry, generate mutated variants, test them in a sandbox, and propose the fittest one for promotion.

When `parse_price("€12,50")` fails, Evolve doesn't just crash. It records a Lesson, spawns variants, keeps the one that passes all examples, the new case, and every invariant, and opens a promotion request with the full diff and lineage. ✅

---

## 🧬 Three heritages

| 🐍 From **Python** | 🔬 From **Julia** | 🦀 From **Rust** |
|---|---|---|
| Indentation, readable syntax | Multiple dispatch | Compiler & runtime written in Rust |
| "Batteries included" stdlib | Broadcasting with `.` | Memory safety, no data races |
| Gradual typing (hints optional) | First-class N-d arrays, linear algebra | Zero-cost FFI to the crates.io ecosystem |
| REPL-first, notebook friendly | Units & uncertainty as types | Cranelift JIT + LLVM AOT backends |
| `import this` philosophy | JIT specialization for speed | WASM sandboxes (wasmtime) for mutations |
| Huge ecosystem (interop via PyO3) | DataFrames as a core type (Arrow) | Fearless concurrency for populations |

### 🔀 Multiple dispatch

```evo
def collide(a: Asteroid, b: Ship):   return damage(b, a.mass)
def collide(a: Ship, b: Asteroid):   return collide(b, a)
def collide(a: Ship, b: Ship):       return bounce(a, b)
```

Dispatch is also how evolution plugs in: a mutated variant is just another **method** with a lineage tag. The runtime routes calls to the currently promoted method.

---

## 🦠 The evolutionary model

Evolve borrows its vocabulary from biology on purpose. The metaphor *is* the mental model.

| | Biology | Evolve concept | What it is |
|:---:|---|---|---|
| 🧬 | Gene | `gene def` | A function that may evolve |
| 🔒 | Conserved gene | `@conserved` | Code that must never mutate (security, money, safety) |
| 🎲 | Mutation | `mutate` | A generated variant: param tweak, AST edit, or agent-proposed patch |
| 🌍 | Environment | `fitness` | Examples, benchmarks, invariants, and a score |
| 🏆 | Natural selection | `select` | Keep the fittest variant(s) that satisfy all invariants |
| 👥 | Population | `population` | Several variants running side by side (A/B, shadow, canary) |
| 🩹 | Scar / immune memory | `Lesson` | A structured record of a failure |
| 🦴 | Fossil record | `.evo/fossils/` | Queryable history of every lesson and mutation |
| 🌳 | Genome / lineage | `.evo/lineage/` | Parent → child ancestry of every promoted variant |
| 🪦 | Extinction | `extinct` | A retired variant, kept for history, never run |
| 🐦 | Speciation | `fork species` | A variant line that diverges for a different environment |

### 🎲 Mutation strategies

1. 🎚️ **Parametric**: tune constants, thresholds, and hyperparameters (cheap, safe).
2. 🌲 **Structural**: AST-level edits from a library of operators (swap branch, widen type, add guard, change algorithm).
3. 🧫 **Recombination**: crossover between two successful variants.
4. 🤖 **Agentic**: an LLM proposes a patch, given the Lesson, the fitness spec, and the lineage.
5. 🧑‍💻 **Human**: a person writes a variant; it enters the same selection pipeline.

### 👥 Explicit populations

```evo
population ranker = evolve(rank_results, size=16, generations=30, seed=42):
    strategy  mutate.parametric | mutate.structural
    fitness   ndcg@10(on="data/queries.parquet") - 0.01 * p99_ms
    shadow    traffic=0.05         # try variants on 5% of real traffic, results discarded

best = ranker.fittest()
best.promote(approve="human")
```

---

## 🧠 Evolve for AI: models, apps, and agent systems

### 🧠 Building next-generation AI models

Gradient descent trains the weights *inside* a model. Evolve adds evolution *outside* it: architectures, modules, hyperparameters, and context-specific variants evolve against fitness that includes **quality, cost, robustness, and safety**. This is the idea behind population-based training, made into language syntax.

```evo
module Encoder(dim: int):                          # 🧩 modular, typed, swappable building block
    layers = [Attention(dim, heads=~8 in 4..16), MLP(dim, ratio=~4 in 2..8)]

gene model Assistant:
    encoder  = Encoder(dim=~1024 in 512..4096)
    memory   = Retrieval(index="kb/")              # 🔌 plug-in modules
    tools    = [search, calculator, robot_arm]     # 🌍 interacts with the world through capabilities
    adapters = species(by=context)                 # 🐦 one specialized line per context: legal, medical, code…
    @conserved safety = SafetyFilter(policy="policies/v3.evo")   # 🔒 never mutated

fitness Assistant:
    evals     "evals/quality/*.jsonl", "evals/robustness/*.jsonl"
    score     = quality - 0.2 * latency_p99 - 0.1 * cost_per_1k
    invariant safety_suite.pass_rate >= 0.99       # 🛡️ a variant that fails safety goes extinct
    invariant not jailbreak_suite.any_success()

train Assistant on data"corpus/" with optimizer=AdamW, evolve=architecture, budget=gpu_hours(500)
```

| Goal | How Evolve supports it |
|---|---|
| ⚡ **Optimized** | Evolution over architectures and hyperparameters; tensor kernels in Rust, with backends such as Burn or Candle |
| 🛡️ **Safe** | `@conserved` safety modules, safety evals as hard `invariant`s, human promotion gates |
| 💪 **Robust** | Robustness and adversarial suites in `fitness`; every production failure becomes a regression Lesson |
| 🌍 **Interacts with the world** | Tools, sensors, and actuators as explicit **capabilities**, sandboxed by default |
| 🔄 **Evolves and adapts to context** | `species(by=context)` plus multiple dispatch on context types |
| 🧩 **Modular** | `module`s with typed interfaces that can be swapped, recombined, and evolved independently |

### 📱 Building AI-native applications

```evo
app SupportDesk:
    gene prompt classify:                          # 💬 prompts are genes, versioned with lineage
        """Classify the ticket as billing, bug, or how-to. Reply with one word."""
    agent resolver = Agent(model=any, tools=[crm.lookup, kb.search])
    memory = evo.fossils(scope="app")            # 🦴 Lessons become long-term memory

    on ticket:
        attempt:
            reply = resolver.solve(ticket, kind=classify(ticket.text))
        learn err:
            remember err
            escalate_to_human(ticket)              # 🚦 imperfect beats absent, humans stay in the loop
```

### 🕸️ Building agent-to-agent systems

```evo
agent Researcher:
    capabilities web.read
    gene def plan(goal: Goal) -> list[Task]: ...

agent Reviewer:
    capabilities none
    def check(report: Report) -> Verdict: ...

@conserved
protocol Review(Researcher -> Reviewer):           # 📜 typed, versioned contract between agents
    send      Report
    reply     Verdict
    invariant every report.claims cite a source

society lab = [Researcher() * 4, Reviewer()]
fitness lab:
    score = verified_findings_per_hour - cost
lab.evolve(roles=true)                             # 🧬 agents evolve; the protocol stays conserved
```

Evolve agents speak **open protocols**: MCP for tools and context, and agent-to-agent protocols such as A2A for cross-system messaging. Protocol messages are typed, Lessons can be shared between agents (with redaction), and the whole society has one lineage.

### 🤖 The language agents learn best in

When agents *write code*, Evolve gives them a real feedback loop:

- 🧾 **Lessons are machine-readable.** Every failure is a typed record that can be exported as JSON or Arrow, not free-form stderr text.
- 📊 **The fossil record is a DataFrame.** Agents (and humans) query their own history:
  ```evo
  fossils = evo.fossils()
  fossils |> filter(_.gene == "parse_price") |> groupby(:error_kind) |> count()
  ```
- 🎯 **Fitness is the reward signal.** Agents don't guess whether a change is better; the language measures it.
- 🔌 **Built-in MCP server.** `evo serve --mcp` exposes lessons, lineage, fitness runs, and mutation proposals as tools, so any agent can join the evolutionary loop.
- 🧪 **Cheap, safe experiments.** Every attempt runs in a sandbox with a budget, so agents can explore freely without breaking anything.
- 🧠 **Memory across sessions.** Lessons persist, so a mistake an agent made last week becomes an immune response today.

---

## 🛡️ Safety: evolution with guardrails

Self-modifying code is powerful and dangerous. Evolve treats safety as part of the language, not an afterthought.

| | Guardrail | Mechanism |
|:---:|---|---|
| 📦 | **Sandboxing** | Mutations are compiled to WASM and run in wasmtime with no ambient authority |
| 🔑 | **Capabilities** | A gene can only touch the network, filesystem, or clock if explicitly granted |
| 📐 | **Invariants** | `invariant` clauses are checked on every variant; violation means instant extinction |
| 🔒 | **Conserved regions** | `@conserved` code (auth, payments, safety limits) is never mutated |
| ⏱️ | **Budgets** | Limits on generations, CPU time, memory, tokens, and money per heal cycle |
| 🚦 | **Promotion gates** | `approve="human"` (default), `"tests"`, or `"auto"` (opt-in, per gene) |
| 🌳 | **Full lineage** | Every promoted variant has a diff, parent, fitness report, and author (human or agent) |
| ⏪ | **Instant rollback** | `evo revert parse_price@gen-7` restores any ancestor |
| 🎰 | **Reproducibility** | Seeded randomness, so evolution runs can be replayed exactly |

> [!IMPORTANT]
> **Default posture:** mutate freely in the sandbox, never change production without a gate.

---

## 🧪 Use cases

See **[docs/use-cases.md](docs/use-cases.md)** for detailed scenarios with code sketches, a prioritization matrix, and applications by industry.

| # | Use case | Why Evolve fits | Priority |
|:---:|---|---|---|
| 1 | 🛠️ **Self-healing data pipelines** | Schema drift and messy input trigger heal cycles instead of 3 a.m. pages | ⭐ Beachhead |
| 2 | 🤖 **AI coding agents that learn** | Lessons + fitness give agents a real feedback loop and long-term memory | ⭐ Beachhead |
| 12 | 🧠 **Next-generation AI models** | Modular, safety-invariant models whose architectures evolve and adapt per context | 🎯 Mission |
| 13 | 📱 **AI-native applications** | Prompts, tools, memory, and evals as language features; apps that learn from every failure | 🎯 Mission |
| 14 | 🕸️ **Agent-to-agent systems** | Typed protocols, conserved contracts, and societies of agents that evolve as a system | 🎯 Mission |
| 3 | 🔗 **Resilient API integrations** | Adapters evolve when a third-party API changes its format | 🔥 High |
| 10 | 💬 **Evolving prompts & agent tools** | Prompts and tool schemas as genes; eval sets as fitness; re-evolve on model upgrades | 🔥 High |
| 4 | 🔬 **Scientific computing & experiments** | Uncertainty, units, arrays, and evolutionary search in one language | 🟡 Medium |
| 5 | 🧮 **Algorithm & heuristic discovery** | Evolve ranking, scheduling, caching, or compression heuristics against benchmarks | 🟡 Medium |
| 6 | 🧠 **ML hyperparameter & architecture search** | Populations + fitness as a native construct, not a framework | 🟡 Medium |
| 11 | 🚨 **Incident auto-remediation** | Runbooks evolve against replayed incidents; Evolve proposes, humans execute | ⏳ Later |
| 7 | 🦾 **Edge, robotics & control tuning** | Parametric evolution of controllers with `@conserved` safety envelopes | ⏳ Later |
| 8 | 🐜 **Simulation & agent-based modeling** | Populations of evolving agents are literally the language model | 🌍 Community |
| 9 | 🎓 **Teaching programming** | Students see failure as data and watch code improve generation by generation | 🌍 Community |

> [!CAUTION]
> **Where Evolve is *not* a good fit (yet):** hard real-time systems, safety-certified software (avionics, medical devices) where any runtime change is forbidden, and tiny scripts where evolution adds nothing. You can still write plain Evolve there; just don't use `gene`.

---

## 🦀 Architecture (built on Rust beta)

Evolve is implemented in **Rust**, tracking the **beta channel** so the compiler can adopt upcoming Rust features (language, `std`, and codegen improvements) one release cycle before stable. CI also builds on stable, so the project never depends on a feature that gets pulled from beta.

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/architecture-dark.svg">
  <img alt="Evolve architecture: .evo source goes through a lossless CST, HIR and typed IR, then to a Cranelift JIT, LLVM AOT, or a WASM sandbox. evo-search edits the CST/IR, receives fitness results from the sandbox, and stores lessons and lineage in the fossil record." src="assets/diagrams/architecture-light.svg" width="100%">
</picture>
</div>

```toml
# rust-toolchain.toml
[toolchain]
channel = "beta"
components = ["rustfmt", "clippy", "rust-src"]
```

<details>
<summary>📦 <b>Planned crate layout</b></summary>

```
evolve/
├── crates/
│   ├── evo-syntax      # lexer + lossless CST (rowan); round-trips source exactly so mutations stay readable
│   ├── evo-hir         # name resolution, desugaring, gene/fitness lowering
│   ├── evo-types       # gradual typing, multiple-dispatch resolution, units & uncertainty types
│   ├── evo-codegen     # Cranelift JIT (dev/REPL) + LLVM AOT (release) + WASM (sandbox)
│   ├── evo-runtime     # memory management, arrays, dispatch tables, attempt/learn
│   ├── evo-data        # Arrow-backed arrays & DataFrames (Polars / arrow-rs)
│   ├── evo-search      # mutation operators, populations, selection, fitness runner
│   ├── evo-sandbox     # wasmtime isolation, capabilities, budgets
│   ├── evo-fossil      # lessons + lineage store (append-only, Arrow/Parquet + SQLite index)
│   ├── evo-agent       # MCP server, LLM mutation providers
│   ├── evo-interop     # Rust FFI, Python (PyO3), C ABI
│   └── evo-cli         # the `evo` command
├── std/                  # standard library, written in Evolve
├── docs/
└── examples/
```

</details>

---

## 🧰 Toolchain sketch

```bash
evo run app.evo                 # ▶️  run (JIT)
evo build --release               # 📦 native binary (AOT)
evo repl                          # 💬 interactive, notebook-friendly
evo test                          # ✅ tests + fitness checks + invariants

evo evolve parse_price            # 🧬 run an evolution cycle for one gene
evo heal --watch                  # 🩹 watch production lessons and propose fixes
evo lessons --gene parse_price    # 🦴 browse the fossil record
evo lineage parse_price           # 🌳 show the family tree of a gene
evo diff parse_price@gen-3 @gen-7 # 🔍 compare two generations
evo promote parse_price@gen-7     # 🚦 human-approved promotion
evo revert parse_price@gen-3      # ⏪ rollback to an ancestor
evo serve --mcp                   # 🔌 expose Evolve to AI agents
```

---

## 🗺️ Roadmap

**Strategy: engine first, language second.** The evolution engine (fossil record, fitness, mutation) ships first as Rust crates with **Python bindings**, so the core idea gets tested with real users before the compiler is finished. The language track runs in parallel, and the two converge in Phase 3.

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/roadmap-dark.svg">
  <img alt="Roadmap timeline: Seed v0.0 Feb 2027, Sprout v0.1 Jun 2027, Root v0.2 Oct 2027, Branch v0.3 Jan 2028, Bloom v0.4 Apr 2028, Pollinate v0.5 Aug 2028, Forest v1.0 H2 2028." src="assets/diagrams/roadmap-light.svg" width="100%">
</picture>
</div>

| Phase | Version | Target | Headline |
|---|---|---|---|
| 🌱 0 **Seed** | `v0.0` | Feb 2027 | Vision, core RFCs, grammar, EvoBench spec |
| 🌿 1 **Sprout** | `v0.1` | Jun 2027 | Evolution engine for Python + Evolve interpreter with `attempt/learn` |
| 🌳 2 **Root** | `v0.2` | Oct 2027 | Arrays, broadcasting, multiple dispatch, DataFrames, units, uncertainty |
| 🌲 3 **Branch** | `v0.3` | Jan 2028 | Native `gene` / `fitness` / `population`, lineage, EvoBench v1 |
| 🌸 4 **Bloom** | `v0.4` | Apr 2028 | Cranelift JIT, WASM sandbox, capabilities, `@heal` in services |
| 🐝 5 **Pollinate** | `v0.5` | Aug 2028 | MCP + A2A, `agent` / `protocol` / `society`, AI-native `app`s, Python interop, LSP |
| 🌍 6 **Forest** | `v1.0` | H2 2028 | LLVM AOT, package manager, stdlib, stability guarantees |

📍 Full plan with deliverables, exit demos, the **EvoBench** benchmark, success metrics, risks, Rust beta policy, and future possibilities (a collective immune system, verified invariants, self-evolving compiler, and more): **[docs/roadmap.md](docs/roadmap.md)**

---

## ❓ Open questions

These are deliberately unresolved. They're the most interesting part. 🤔

1. 🏷️ **Typing:** how gradual? Should `gene` functions require full type signatures so mutations have a contract?
2. 🧠 **Memory model:** tracing GC, reference counting, or Rust-style ownership hidden behind Python-like syntax?
3. 🔢 **Indexing:** 0-based (Python) or 1-based (Julia)? *(Leaning 0-based.)*
4. 📍 **Where does evolution happen?** Only at dev time, in staging, or live in production with shadow traffic?
5. 🎯 **Fitness gaming:** how do we stop variants from overfitting the examples (Goodhart's law)? Hidden holdout sets? Adversarial examples generated from Lessons?
6. 🎰 **Determinism:** can agentic (LLM) mutations be made reproducible enough for audits?
7. 🪞 **Identity:** after 50 generations, is it still "the same" function? How should semver work for evolving code?
8. ⚖️ **Ownership & licensing:** who is the author of code written by evolution?
9. 🔐 **Lesson privacy:** Lessons capture inputs. How do we redact PII by default?
10. 🌐 **Ecosystem sharing:** should Lessons be shareable across projects, like a global immune system?

💬 Have an opinion? [Open an RFC issue](https://github.com/peace-program-project/peace/issues/new/choose).

---

## 🤝 Contributing

Evolve is at the idea stage, so the best contributions now are **use cases, syntax ideas, real-world failure cases for EvoBench, and hard questions**.

| If you want to… | Do this |
|---|---|
| 💡 Propose a language idea | Read the [draft RFCs](rfcs/README.md), then open an **RFC** issue |
| 🧪 Share a real-world failure | Open a **EvoBench case** issue (format: [bench/README.md](bench/README.md)) |
| 🌍 Describe a use case | Open a **Use case** issue |
| ❓ Ask anything | Start a [Discussion](https://github.com/peace-program-project/peace/discussions) |

Read **[CONTRIBUTING.md](CONTRIBUTING.md)** and [how to help right now](docs/roadmap.md#10-how-to-help-right-now). Everyone participating agrees to our **[Code of Conduct](CODE_OF_CONDUCT.md)**. 🕊️

---

## 📄 License

Evolve is licensed under the **[Apache License, Version 2.0](LICENSE)**. See [NOTICE](NOTICE).

Unless you explicitly state otherwise, any contribution you intentionally submit for inclusion in Evolve is licensed under Apache-2.0, as defined in the license, without any additional terms or conditions.

---

<div align="center">

<img src="assets/logo/evolve-mark.svg" width="72" alt="Evolve logo"/>

<i>"Nothing in biology makes sense except in the light of evolution."</i> (Theodosius Dobzhansky)<br/>
<b><i>Nothing in Evolve makes sense except in the light of failure.</i></b> 🧬

<sub>Made with 🕊️ by the <a href="https://github.com/peace-program-project">Evolve Program Project</a></sub>

</div>
