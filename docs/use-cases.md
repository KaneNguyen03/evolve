# Peace: Use Cases

> A thinking document. Each scenario covers **the pain today**, **how Peace changes it**, a **code sketch**, and the **open questions** it raises. Syntax is illustrative and will change.

---

## 1. Self-healing data pipelines

### The pain today
A vendor renames `customer_id` to `customerId`, or starts sending dates as `21/11/2026` instead of `2026-11-21`. The nightly ETL crashes, someone gets paged, writes a one-line fix, and redeploys. Next month it happens again with a different column.

### With Peace
The parsing and mapping steps are `gene`s. When they fail, the runtime records a Lesson with the offending rows, generates variants (for example, "accept a camelCase alias" or "try an alternate date format"), validates them against historical data plus the new rows, and queues the fittest one for approval. Meanwhile the failing rows go to quarantine, so the rest of the batch still lands.

```peace
schema Order:
    customer_id: str
    ordered_at:  Date
    total:       Money
    invariant total.amount >= 0

@heal(strategies=[mutate.structural, ask_agent], budget=30, approve="human")
gene def normalize(raw: DataFrame) -> DataFrame[Order]:
    return raw
      |> rename(customerId="customer_id")
      |> with(ordered_at = Date.parse.(_.ordered_at, "%Y-%m-%d"))

fitness normalize:
    examples  history("orders", days=90)        # last 90 days of good batches
    score     = rows_valid / rows_total
    invariant schema_matches(result, Order)

pipeline nightly:
    attempt:
        orders = normalize(read"s3://vendor/orders/today.csv")
    learn err:
        remember err
        quarantine(err.bad_rows)                # imperfect beats absent: ship the good rows
        orders = err.partial_result
    orders |> write"warehouse://orders"
```

### Open questions
- How much historical data is "enough" fitness to trust a schema mutation?
- Should quarantined rows be retried automatically once a variant is promoted?

---

## 2. AI coding agents that actually learn

### The pain today
An agent writes code, runs it, sees a stack trace, edits, and runs again. Across sessions it forgets everything. The same mistakes (wrong API version, off-by-one, missing null check) come back in every new task. Success is judged by "tests pass?", a single bit.

### With Peace
- Every failure is a typed **Lesson** the agent can query, not just read.
- **Fitness** is a continuous reward signal (accuracy, latency, memory, cost), so the agent can tell "better" from "merely passing".
- The **fossil record** is long-term memory that persists across sessions and agents.
- `peace serve --mcp` gives the agent tools such as `lessons.query`, `gene.mutate`, `fitness.run`, and `lineage.show`.

```peace
# What an agent can ask before writing new code:
past = peace.fossils()
  |> filter(_.module == "billing" and _.kind == "TypeError")
  |> select(:message, :fix_diff, :fitness_delta)
  |> sort(:fitness_delta, rev=true)
  |> first(5)
```

The agent sees which fixes worked before and by how much, then proposes a mutation. The language runs it in a sandbox and scores it. Selection is objective and lineage is automatic.

### Open questions
- Should Lessons from one agent be shared with others by default (a "collective immune system")?
- How do we stop an agent from gaming the fitness function?

---

## 3. Resilient third-party API integrations

### The pain today
Integrations break silently when a partner adds a field, changes an enum, or paginates differently. Fixes are reactive and manual.

### With Peace
Adapters are genes whose fitness comes from **contract examples** (recorded real responses) plus invariants about the domain model. A failure triggers a heal cycle against freshly recorded responses. Because the `http` capability is granted only to the fetch step, a mutation in the parser can never start calling the network.

```peace
@conserved                               # auth logic never mutates
def sign(req: Request) -> Request: ...

@capabilities(none)                      # pure parsing, no I/O allowed
@heal(strategies=[mutate.structural], approve="tests")
gene def parse_shipment(json: Json) -> Shipment: ...

fitness parse_shipment:
    examples  recorded"contracts/carrier-x/*.json"
    invariant result.weight > 0 kg
```

### Open questions
- Is `approve="tests"` acceptable for pure parsers with strong invariants, while I/O code always needs a human?

---

## 4. Scientific computing with honest uncertainty

### The pain today
Scientists juggle NumPy, pandas, a units library, an uncertainty library, and a separate optimization framework. Units and error bars get lost between libraries. Exploring model variants means copy-pasted notebooks.

### With Peace
Units and uncertainty are part of the type system. Arrays and DataFrames are native. Model exploration is a `population`.

```peace
data = read"lab/pendulum.csv"            # columns carry units from the header

gene def model(L: m, θ0: rad) -> s:
    return 2π * sqrt(L / g) * (1 + θ0^2 / 16)

fitness model:
    examples  data[:, [:L, :θ0]] => data[:, :period]
    score     = -chi2(result, expected)  # uncertainty-weighted

pop = evolve(model, size=32, generations=50, strategy=mutate.structural, seed=7)
print(pop.fittest().source)              # readable formula, not a black box
print(pop.fittest().fitness)             # e.g. χ²/ν = 1.04 ± 0.12
```

Evolution here is *symbolic regression*: the result is a readable formula you can publish, with a lineage that shows how it was found.

### Open questions
- How do we keep structural mutations dimensionally consistent? (Units typing should reject `m + s` automatically.)

---

## 5. Algorithm and heuristic discovery

### The pain today
Cache eviction, job scheduling, query planning, and compression levels are tuned by hand once and then left alone, even though workloads keep drifting.

### With Peace
Heuristics are genes with benchmark-driven fitness, evolved offline against recorded workloads and promoted with a human gate.

```peace
gene def evict_score(entry: CacheEntry, now: Time) -> f64:
    return entry.hits / (now - entry.last_access).seconds

fitness evict_score:
    benchmark replay"traces/prod-2026-11.trace"
    score     = hit_rate - 0.1 * p99_latency_ms
    invariant result.is_finite()
```

### Open questions
- How do we avoid overfitting to one trace? Rotate traces per generation? Keep a holdout trace?

---

## 6. ML hyperparameter and architecture search

### The pain today
You need Optuna, Ray Tune, W&B, and glue code. Search spaces live in YAML, separate from the model code.

### With Peace
The search space lives next to the code as mutable parameters (`~` marks an evolvable constant with a range).

```peace
gene def train(data: Dataset) -> Model:
    lr     = ~0.001  in 1e-5..1e-1 log
    layers = ~4      in 2..12
    drop   = ~0.1    in 0.0..0.5
    return mlp(layers=layers, dropout=drop).fit(data, lr=lr, epochs=20)

fitness train:
    score = val_accuracy(result) - 0.01 * params_millions(result)
```

### Open questions
- Should Peace integrate with existing trackers (MLflow, W&B) or treat the fossil record as the tracker?

---

## 7. Edge, robotics, and control tuning

### The pain today
Controller gains are tuned in the lab, then the robot meets a new floor surface, payload, or temperature. Retuning means a technician visit.

### With Peace
Only *parametric* mutation is allowed in the field, inside a `@conserved` safety envelope enforced by invariants. New gains are evaluated in simulation or shadow mode before they control the actuator.

```peace
@conserved
def safety_envelope(cmd: Torque) -> Torque:
    return clamp(cmd, -5 N*m, 5 N*m)

@evolve(strategy=mutate.parametric, where="shadow", approve="tests")
gene def pid(err: rad, derr: rad/s) -> Torque:
    return ~1.2 * err + ~0.05 * derr

fitness pid:
    simulate  "sim/arm.urdf" with disturbances
    score     = -settling_time - 10 * overshoot
    invariant abs(result) <= 5 N*m
```

### Open questions
- Can the WASM sandbox meet the latency budget on microcontrollers, or does field evolution only run on a companion computer?

---

## 8. Simulation and agent-based modeling

### The pain today
Evolutionary simulations (ecology, economics, game AI) reimplement genomes, mutation, and selection from scratch every time.

### With Peace
The simulation agents *are* Peace genes. The language's evolution engine is the simulation's evolution engine.

```peace
species Forager:
    gene def decide(self, view: Grid) -> Action: ...

world = World(size=(200, 200), food=0.05)
pop   = population(Forager, size=500)

for epoch in 0..1000:
    world.step(pop)
    pop = pop.select(top=0.2).reproduce(mutate.structural, rate=0.02)

pop.lineage().plot()                     # phylogenetic tree of strategies
```

---

## 9. Teaching programming

### The pain today
Beginners experience errors as personal failure. Red text means "you're bad at this".

### With Peace
The language's culture says failure is data. Students:
- see their Lessons as a personal learning log (`peace lessons --mine`),
- watch a function improve generation by generation,
- learn testing naturally, because fitness *is* testing,
- learn about evolution, statistics, and uncertainty along the way.

---

## Anti-use-cases (where to be careful)

| Scenario | Why caution | Recommendation |
|---|---|---|
| Certified safety software (avionics, medical) | Runtime change can void certification | Plain Peace only; no `gene` in shipped code |
| Hard real-time loops | Dispatch and sandbox overhead | Evolve offline, compile AOT, freeze |
| Security & cryptography | Mutation could weaken guarantees | Always `@conserved` |
| Legal or financial calculations | Auditability and explainability | `approve="human"` and mandatory lineage review |

---

## How to add a use case

Copy this template into a new section or an issue:

```markdown
## N. <Title>
### The pain today
### With Peace
<code sketch>
### Open questions
```
