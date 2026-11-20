---
rfc: 0001
title: Core syntax
status: draft
authors: [peace-program-project]
created: 2026-11-21
phase: Seed → Sprout
requires: []
spec: [spec/grammar.ebnf]
---

# RFC 0001: Core syntax

## Summary

Peace's surface syntax is **Python-shaped** (indentation, `def`, f-strings, readable keywords) with a small set of **Julia-style additions** for data work (broadcasting, `^`, symbols, string macros, `|>`) and **Peace-specific constructs** for evolution (`gene`, `fitness`, `attempt / learn`, `remember`). This RFC fixes the lexical rules, statements, expressions, and operator precedence for the Phase 1 interpreter. The grammar lives in [`spec/grammar.ebnf`](../spec/grammar.ebnf).

## Motivation

The Phase 1 parser (`peace-syntax`) needs a frozen target. Every code sample in the docs should parse under this RFC. Where the docs disagree with each other, this RFC decides.

Design rule: **if a Python programmer can guess what a line does, keep it. If a Julia user would miss a data feature, add it with the smallest syntax possible.**

## Guide-level explanation

```peace
import std.data as data

def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)

gene def parse_price(raw: str) -> Money:
    return Money.parse(raw.strip(), currency="USD")

attempt:
    prices = data.read"prices.csv" |> map(_.raw |> parse_price)
learn ParseError as err:
    remember err
    prices = []
always:
    log("done")

ys = sin.(xs) .+ 1                # broadcasting
sq = x -> x ^ 2                   # lambda
by_month = sales |> groupby(:month) |> sum(:revenue)
```

What a Python user needs to unlearn:

| Python | Peace | Why |
|---|---|---|
| `True`, `False`, `None` | `true`, `false`, `none` | Consistent lowercase keywords |
| `x ** 2` | `x ^ 2` | Julia/math convention; `**` is an error with a hint |
| `lambda x: x + 1` | `x -> x + 1` | Shorter, readable in pipelines |
| `try / except / finally` | `attempt / learn / always` | Failures are recorded as Lessons (see RFC 0002) |
| `range(0, 10)` | `0..10` | Range literal (half-open) |

## Reference-level explanation

### Lexical structure

- **Encoding:** UTF-8 source, file extension `.peace`.
- **Indentation:** blocks open with `:` and an indented suite. Indent unit is consistent spaces per file (4 recommended). **Tabs in indentation are a lex error.**
- **Comments:** `#` to end of line. Doc comments: a string literal as the first statement of a `def`, `gene`, `module`, `agent`, or `app` body.
- **Identifiers:** Unicode `XID_Start XID_Continue*` (so `β`, `θ0`, `π` are valid). Identifiers starting with `_` are private to their module.
- **Line joining:** inside `()`, `[]`, `{}` newlines are ignored. A line ending in a binary operator or `|>` also continues, and so does a line *starting* with `|>` (pipeline style used throughout the docs).

### Keywords

**Reserved:** `and as attempt always break continue def elif else false for from gene if import in is learn module none not or pass remember return true while fitness population species agent protocol society app model schema`

**Contextual** (keywords only inside the block that defines them, ordinary identifiers elsewhere): `examples holdout score invariant strategy shadow benchmark simulate replay capabilities send reply timeout train evolve with on`

### Literals

| Kind | Examples | Notes |
|---|---|---|
| Integer | `42`, `1_000_000`, `0xFF`, `0b1010` | Arbitrary precision `int`; sized types via annotation |
| Float | `3.14`, `1e-5`, `2.5e3` | 64-bit default |
| Unit-suffixed number | `9.81 m/s²`, `5 N*m`, `12.5 kg` | A numeric literal followed by a **unit expression**; resolved by RFC 0005 |
| Uncertain number | `9.81 ± 0.02`, ASCII `9.81 +/- 0.02` | `±` is a binary operator, see precedence |
| String | `"a"`, `'a'`, `"""multi"""`, `f"{x}"` | Python semantics, f-strings included |
| String macro | `read"sales.csv"`, `data"corpus/"` | `ident"..."` with no space calls the macro `ident` at compile time (Julia-style non-standard string literal) |
| Symbol | `:month`, `:revenue` | Interned names, used for columns and keys |
| Range | `0..10`, `0..=10`, `1e-5..1e-1` | `..` half-open, `..=` closed |
| Collections | `[1, 2]`, `{"k": 1}`, `{1, 2}`, `(1, 2)` | list, dict, set, tuple |
| Evolvable constant | `~0.001 in 1e-5..1e-1 log`, `~8 in 4..16` | Marks a mutable parameter of the enclosing `gene` (RFC 0003). Ranges after `in` are **closed search intervals** |

### Statements

```
def NAME(params) [-> Type]: suite          # function (one method of a generic function)
gene def NAME(params) [-> Type]: suite     # evolvable function (RFC 0003)
fitness NAME: clauses                      # fitness spec for a gene (RFC 0003)
attempt: suite (learn [Type as] NAME: suite)+ [always: suite]
remember EXPR                              # record a Lesson (RFC 0002)
if / elif / else, for NAME in EXPR, while, break, continue, pass, return
import a.b [as c] | from a.b import c [as d]
@decorator(args) before def / gene def / module / agent
```

`attempt` semantics: run the suite; on failure, match `learn` clauses top to bottom (`learn err:` with no type catches everything). `always` runs on every path. A `learn` clause **without** `remember` still produces a Lesson with `recorded=false` in debug builds so the failure is never silently lost (see RFC 0002).

### Expressions and precedence

From lowest to highest:

| Level | Operators | Assoc. |
|---|---|---|
| 1 | `->` (lambda) | right |
| 2 | `\|>` (pipe) | left |
| 3 | `or` | left |
| 4 | `and` | left |
| 5 | `not` | prefix |
| 6 | `== != < <= > >= in not in is is not` | chained, like Python |
| 7 | `..` `..=` | none |
| 8 | `±` `+/-` | left |
| 9 | `+ -` and `.+ .-` | left |
| 10 | `* / \ %` and `.* ./ .\` | left |
| 11 | unary `- +` | prefix |
| 12 | `^` and `.^` | **right** |
| 13 | call `f(x)`, broadcast call `f.(x)`, index `a[i]`, attribute `a.b`, string macro | left |

- **Pipe:** `x |> f` is `f(x)`. `x |> f(a, b)` is `f(x, a, b)`: the left value becomes the **first** argument.
- **Placeholder `_`:** inside a call argument, an expression containing `_` becomes a one-argument lambda scoped to the **smallest enclosing call argument**. `filter(_.region == "EU")` is `filter(r -> r.region == "EU")`.
- **Broadcasting:** a dot before an operator or before a call's parenthesis applies it element-wise, with shapes broadcast by RFC 0005.
- **Indexing is 0-based**, slices are half-open `a[1:3]`, negative indices count from the end (Python semantics).

### Multiple dispatch

All `def`s with the same name visible in a module are **methods of one generic function**. Calls dispatch on the runtime types of **all** positional arguments, choosing the most specific method; ambiguity is a compile-time error when detectable, otherwise a runtime `AmbiguityError` (recorded as a Lesson).

## Safety and failure modes

- **Parse errors are Lessons too.** The parser is error-tolerant (lossless CST), reports every error with a fix hint, and the REPL records them for the learner (`peace lessons --mine`).
- **Mutations operate on the CST**, never on text, so an evolved variant always round-trips to valid, formatted source.

## Drawbacks

- `true/false/none` and `^` break muscle memory for Python users. Mitigation: the parser recognizes the Python spellings and emits a one-line hint.
- `_` placeholder scoping is a classic source of confusion (Scala). The "smallest enclosing call argument" rule is simple but must be taught early.

## Alternatives

- **Python-exact syntax** (`**`, `True`, `lambda`): maximal familiarity, but clashes with Julia-style math and the pipeline style used across the docs.
- **Braces instead of indentation:** easier to parse, but abandons the Python heritage.

## Prior art

Python (indentation, f-strings, chained comparisons), Julia (broadcast dots, `^`, symbols, non-standard string literals), Elixir and F# (`|>`), Scala (`_` placeholder), Rust (`..` and `..=` ranges).

## Unresolved questions

1. Should `..` in a `for` header and `..` in an evolvable range (`~x in a..b`, closed) use one notation? Proposal on the table: always half-open, and evolvable ranges use `a..=b`.
2. Unit suffix parsing: is `5 m` (space-separated) unambiguous enough, or do we require a marker (`5[m]`)?
3. `class` vs. `struct` vs. `schema`: which record types exist in Phase 1? (Leaning: `schema` for validated data records, `struct` for plain records, no inheritance.)

## Test plan

- A conformance corpus in `tests/syntax/` with one `.peace` file per construct, plus every code block from `README.md` and `docs/` extracted and parsed in CI.
- Round-trip test: `parse → CST → print` must reproduce the input byte for byte.
- Error-recovery tests: each malformed input yields a specific diagnostic and a usable CST.
