---
rfc: 0005
title: "Data model: arrays, frames, units, uncertainty"
status: draft
authors: [peace-program-project]
created: 2026-11-21
phase: Root
requires: [0001]
spec: []
---

# RFC 0005: Data model: arrays, frames, units, uncertainty

## Summary

Defines Peace's core data types: **scalars**, **N-dimensional arrays** with broadcasting, **DataFrames** on Apache Arrow, **units of measure**, **uncertain values**, and **missing data**. These types live in the core language, not in libraries, so they compose: an array of uncertain lengths in meters inside a DataFrame column just works.

## Motivation

Today a scientist combines NumPy, pandas, pint, and uncertainties, and the four don't know about each other. Peace's data missions (scientific computing, ML, AI models) need one coherent model with Julia-level speed.

## Guide-level explanation

```peace
g  = 9.81 ± 0.02 m/s²                 # uncertain scalar with a unit
L  = [0.50, 0.75, 1.00] m             # array with a unit
T  = 2 * π .* sqrt.(L ./ g)           # units and uncertainty propagate: T is in s
df = DataFrame(L=L, T=T)
df |> filter(_.T > 1.5 s) |> select(:L)

x = [1.0, missing, 3.0]
mean(x)                               # missing (propagates)
mean(skipmissing(x))                  # 2.0
```

## Reference-level explanation

### Scalars

`bool`, `int` (arbitrary precision), sized `i8…i64`, `u8…u64`, `f32`, `f64` (default `float`), `complex`, `str`, `bytes`, `Date`, `Time`, `Duration`, `Decimal`, `Money` (decimal + currency). Integer overflow on sized types is an error (Lesson), not a wrap, unless using `wrapping_*` functions.

### Arrays

- `Array[T, N]`: dense, homogeneous, **row-major** by default (NumPy and Arrow compatible), with strided views. `a.T` is a view.
- Literals: `[1, 2, 3]` is a 1-d array when all elements are numeric, otherwise a `list`. 2-d literal: `[1 2; 3 4]` (Julia style).
- **Broadcasting** follows NumPy rules: align shapes from the right; dimensions match if equal or one of them is 1.
- **Dot fusion:** `sin.(x) .+ 1` compiles to a single loop with no temporaries (Julia's broadcast fusion).
- Linear algebra in `std.linalg`: `A * B` is matrix multiply for 2-d arrays, `A \ b` solves, `.*` is element-wise.
- Backing storage is an Arrow-compatible buffer so arrays move into DataFrames without copying.

### DataFrames

- `DataFrame` is a table of named, typed, Arrow-backed columns. `DataFrame[Schema]` checks columns against a `schema` (RFC 0001) at the boundary.
- Verbs: `filter`, `select`, `with` (add or replace columns), `groupby`, `agg` and the reducers (`sum`, `mean`, `count`, …), `join`, `sort`, `first`, `rename`. All work with `|>`.
- Execution is **lazy** inside a pipeline and materialized at the end, with a query optimizer (backed by Polars or DataFusion, decided in implementation).
- I/O macros: `read"…"` and `write"…"` infer format from the extension (`.csv`, `.parquet`, `.json`, `.arrow`) or URI scheme (`s3://`, `warehouse://` via plugins).

### Units of measure

- A unit is a type-level **dimension vector** over the 7 SI base dimensions plus a scale. `Quantity[f64, m/s]`.
- Arithmetic checks dimensions at compile time where types are known and at runtime otherwise. `1 m + 1 s` is a type error. `1 km + 1 m == 1001 m`.
- Conversions are explicit: `x |> to(km)`. Dimensionless results drop the unit.
- Units work element-wise on arrays and per column in DataFrames (column metadata).

### Uncertainty

- `a ± b` creates `Uncertain[T]` with standard deviation `b`.
- **Phase 2 semantics:** first-order (linear) error propagation, tracking **correlations** between values derived from the same source (like Python's `uncertainties`, so `x - x == 0 ± 0`).
- Monte Carlo propagation is available explicitly: `propagate(f, x, method=:montecarlo, n=10_000)`.
- Comparisons on uncertain values are errors unless explicit: `prob(x > y)` or `nominal(x) > nominal(y)`.

### Missing data

- `missing` is a value of type `Missing`. `T | Missing` is written `T?`.
- Arithmetic propagates `missing` (Julia semantics). Reducers propagate unless the input is wrapped in `skipmissing`.
- In DataFrames, nullability uses the Arrow validity bitmap, so `T?` columns cost one bit per row.

## Safety and failure modes

- Dimension errors, shape mismatches, and invalid uncertainty comparisons all raise typed errors that become Lessons with the offending shapes and units (never values, unless sampling is on).
- Evolved variants must keep unit-correct types: a structural mutation that produces `m + s` is rejected at type-check time, which prunes the search space for free.

## Drawbacks

- Row-major breaks with Julia (column-major) and may surprise Julia users doing linear algebra. Chosen for Python, NumPy, and Arrow interop.
- Type-level units make error messages harder. Needs careful diagnostics.

## Alternatives

- **Column-major arrays** (Julia, Fortran): better for some linear algebra, worse for interop.
- **Units as a library:** simpler compiler, but loses compile-time checks and mutation pruning.

## Prior art

NumPy (broadcasting), Julia (dot fusion, `missing`, column-major arrays), Apache Arrow and Polars (columnar frames, lazy queries), F# units of measure, Unitful.jl, Measurements.jl and Python `uncertainties` (correlated propagation).

## Unresolved questions

1. Polars vs. DataFusion as the query engine.
2. Is `[1 2; 3 4]` worth the parsing complexity, or is `array([[1, 2], [3, 4]])` enough?
3. How are units declared by libraries (custom units like `USD` or `tokens`)?

## Test plan

- NumPy conformance tests for broadcasting shapes.
- Unit algebra property tests (associativity, conversion round-trips).
- Uncertainty propagation compared against Python `uncertainties` on a shared corpus.
- The pendulum example from [use case 4](../docs/use-cases.md#4-scientific-computing-with-honest-uncertainty) as an end-to-end test.
