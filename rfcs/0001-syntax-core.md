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

Peace's syntax looks like Python: indentation, `def`, f-strings, comprehensions, and readable keywords. It adds a small set of Julia-style features for data work: broadcasting, `^`, symbols, string macros, and `|>`. It also adds Peace's own constructs for evolution: `gene`, `fitness`, `attempt / learn`, and `remember`.

This RFC fixes the lexical rules, keywords, statements, expressions, operator precedence, and diagnostics for the Phase 1 interpreter. The grammar lives in [`spec/grammar.ebnf`](../spec/grammar.ebnf). It is written in the same PEG-style notation as the [Python 3.16 grammar](https://docs.python.org/3.16/reference/grammar.html).

Revision 2 went through the [Python 3.16 language reference](https://docs.python.org/3.16/reference/index.html) section by section. For each Python rule it records whether Peace adopts it, adapts it, declines it, or defers it, and why ([Lessons from Python](#lessons-from-python-316)).

## Motivation

The Phase 1 parser (`peace-syntax`) needs a frozen target. Every code sample in the docs should parse under this RFC. Where the docs disagree with each other, this RFC decides.

Design rule: **if a Python programmer can guess what a line does, keep it. If a Julia user would miss a data feature, add it with the smallest syntax possible.** Thirty years of Python also show which rules cost the most to fix later, such as hard keywords, silent escapes, and implicit concatenation. Peace has no users to break yet, so this RFC fixes those now.

## Guide-level explanation

```peace
from std.data import read

def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)

gene def parse_price(raw: str) -> Money:
    return Money.parse(raw.strip(), currency="USD")

attempt:
    prices = read"prices.csv" |> map(_.raw |> parse_price)
learn ParseError as err:
    remember err
    prices = []
always:
    log("done")

ys = sin.(xs) .+ 1                # broadcasting
sq = x -> x ^ 2                   # lambda
by_month = sales |> groupby(:month) |> sum(:revenue)
```

Revision 2 adds the Python constructs a Python programmer reaches for first:

```peace
from std.io import (open, write)

model = load("pendulum.onnx")                 # `model` is a soft keyword: still a normal name here
evens = [x ^ 2 for x in 0..10 if x % 2 == 0]
by_id = {r.id: r for r in rows}
label = "hot" if temp > 30 else "ok"
first, *rest = sorted(xs)
mid = len(xs) // 2

def fetch(url: str, *, retries: int = 3, **headers) -> Response:
    assert retries >= 0, "retries must be non-negative"
    if not url:
        raise ValueError("empty url")
    with open(url) as conn, timer() as t:
        return conn.read(**headers)

ok = 0 <= p <= 1
```

What a Python user needs to unlearn:

| Python | Peace | Why |
|---|---|---|
| `True`, `False`, `None` | `true`, `false`, `none` | Consistent lowercase keywords |
| `x ** 2` | `x ^ 2` | Julia and math convention. `**` is an error with a hint, except as `**kwargs` |
| `lambda x: x + 1` | `x -> x + 1` | Shorter, readable in pipelines |
| `try / except / finally` | `attempt / learn / always` | Failures are recorded as Lessons (RFC 0002) |
| `range(0, 10)` | `0..10` | Range literal (half-open) |
| `a @ b` | `a * b` | `*` is matrix multiply for 2-d arrays, `.*` is element-wise (RFC 0005) |
| `"a" "b"` | `"a" + "b"` | No implicit string concatenation |
| `x < y > z` | `x < y and z < y` | Comparison chains must keep one direction |
| `a = 1; b = 2` | two lines | One statement per line |

## Reference-level explanation

### Lexical structure

**Source text.**
- Source files are UTF-8 with the extension `.peace`. There is no encoding declaration.
- A byte-order mark is allowed only at offset 0, where it is kept as trivia.
- Lines end in LF or CRLF. A lone CR is an error.
- The NUL character is an error anywhere.

**Bidirectional controls.** The characters U+202A to U+202E and U+2066 to U+2069 are an error anywhere in source, including strings and comments. Inside a string, write them as escapes such as `"‮"`. Human review is the promotion gate (RFC 0004), so code must display the way it runs. This rule closes the "Trojan Source" attack.

**Comments.** A comment runs from `#` to the end of the line. A doc comment is a string literal as the first statement of a `def`, `gene`, or `module` body, or of a declaration block from a later RFC.

**Logical lines.** Each statement ends at a NEWLINE token. Physical lines join into one logical line in three cases:
1. inside `()`, `[]`, or `{}`;
2. after a line that ends in a binary operator (`+ - * / // \ % ^ | |> ± and or == != < <= > >=` and the dotted forms);
3. before a line whose first token is `|>` (pipeline style).

There is **no backslash continuation**. `\` is left division (RFC 0005). Blank and comment-only lines produce no NEWLINE.

**Indentation.**
- A block opens with `:` and an indented suite.
- Only spaces may indent. **A tab in indentation is an error**; Python's tab-width rules are not needed.
- The indent stack works as in Python: it starts at `[0]`, a deeper line pushes and emits INDENT, and a shallower line pops and emits one DEDENT per level.
- A shallower line that matches no level on the stack is an error ("unindent does not match any outer level"). So is an indented first line ("unexpected indentation").
- At end of file, every open level closes.

**Identifiers.**
- An identifier is `XID_Start XID_Continue*`, and `_` may also start one, so `β`, `θ0`, and `π` are valid.
- Superscript digits and `⁻` never belong to an identifier. They are unit powers, so `s²` is `s` followed by `²`.
- Identifiers are compared after **NFC** normalization, not Python's NFKC: NFKC would fold `ℝ`, `𝐱`, and `x²` into `R`, `x`, and `x2`, which matter in math-heavy code. The CST keeps the original spelling.
- A leading `_` makes a name private to its module.
- Peace reserves no `__dunder__` names: operators are methods of generic functions (see [Multiple dispatch](#multiple-dispatch)).

**`_` has exactly three roles**:
1. in a target (`for _ in 0..3`, `a, _ = pair`) it discards the value;
2. inside a call argument it is the placeholder (see [Expressions](#expressions-and-precedence));
3. anywhere else, reading `_` is an error.

**Numbers.**

| Kind | Examples | Rules |
|---|---|---|
| Integer | `42`, `1_000_000`, `0xFF`, `0o17`, `0b1010` | `_` only between digits, or once right after `0x`, `0o`, `0b` (`1__0`, `_1`, `1_` are errors). No leading zeros: `0123` is an error with the hint `0o123`. Arbitrary-precision `int`; sized types come from annotations |
| Float | `3.14`, `1e-5`, `2.5e3` | Digits on **both** sides of `.`: `.5` and `5.` are errors with the hints `0.5` and `5.0`, because `.` and `..` are operators in Peace. 64-bit by default |

- A number directly followed by a letter or `_` is an error, so `5kg` gives the hint "write `5 kg`" and `2π` gives "write `2 * π`". Python 3.16 is moving the same way for `1or x`.
- Units are written after a space (`9.81 m/s²`) and resolved by RFC 0005.
- There is no imaginary suffix. Complex numbers come from RFC 0005.

**Strings.**
- Strings use `'…'`, `"…"`, `'''…'''`, or `"""…"""`.
- Escapes are Python's set: `\\ \' \" \n \r \t \0 \xhh \uXXXX \UXXXXXXXX \N{name}` and `\` followed by a newline. Any other escape is an **error**, not a kept backslash. Python warns about unknown escapes today and plans to make them errors. These rules apply to plain strings and to `f`, `t`, and `b` literals. `r"…"` and user string macros receive the raw text, and the macro interprets it.
- Two string literals next to each other are an error with the hint "missing comma, or use `+`". Implicit concatenation hides a missing comma in lists.

**String prefixes are built-in string macros.** `ident"…"` with no space calls the macro `ident` at compile time, as Julia's non-standard string literals do. The built-ins are:

| Literal | Meaning |
|---|---|
| `f"…{expr}…"` | Format string. Follows Python 3.12 (PEP 701): the inner expression may reuse the outer quote and may nest. A replacement field may span lines, and hold comments, only in a triple-quoted f-string. Supports `{x=}`, `!r`, and `{x:.2f}` |
| `t"…{expr}…"` | Template (PEP 750): a value holding the static parts and the interpolated values separately |
| `r"…"` | Raw: no escapes |
| `b"…"` | Bytes: ASCII only |

A user macro such as `sql"…"`, `read"…"`, or `prompt"…"` that interpolates receives a **template, never a pre-joined string**. Quoting and escaping are the macro's job, so prompt and SQL injection cannot happen by string concatenation.

**Other literals.**

| Kind | Examples | Notes |
|---|---|---|
| Uncertain number | `9.81 ± 0.02`, ASCII `9.81 +/- 0.02` | `±` is a binary operator, see precedence |
| Symbol | `:month`, `:revenue` | Interned names for columns and keys. `:` followed by a name **with no space** is always a symbol, also inside `[...]`: `df[:, :period]` selects a column. A slice up to a variable is written `xs[0:n]` or `xs[: n]` |
| Ellipsis | `...` | Placeholder expression, mainly for bodies: `def charge(card: Card) -> Receipt: ...` |
| Range | `0..10`, `0..=10`, `1e-5..1e-1` | `..` is half-open, `..=` is closed |
| Collections | `[1, 2]`, `{"k": 1}`, `{1, 2}`, `(1, 2)`, `(1,)` | list, dict, set, tuple. `{}` is an empty dict; an empty set is `set()`. Only the comma makes a tuple |
| Evolvable constant | `~0.001 in 1e-5..1e-1 log`, `~8 in 4..16` | Marks a mutable parameter of the enclosing `gene` (RFC 0003). Ranges after `in` are **closed search intervals** |

**Operators and delimiters.**
- Matching is longest first ("maximal munch"), as in Python.
- `` ` ``, `$`, `?`, and `!` outside `!=` and f-string conversions are errors.
- The parser gives hints for `&&`, `||`, and `!x`: use `and`, `or`, and `not`.
- **Bitwise operators** (`& | ^ ~ << >>` in Python) do not exist in Phase 1. `^` is power, `|` joins type unions, and `~` marks evolvable constants. Bit operations are the functions `band`, `bor`, `bxor`, `shl`, and `shr`.

### Keywords

Peace follows Python's lesson from `match` (3.10), `type` (3.12), and `lazy` (3.15): **new keywords are soft**. A soft keyword acts as a keyword only where the grammar expects it and is an ordinary name everywhere else, so adding one never breaks code. Python had to break code to make `async` hard in 3.7. Soft keywords spare Peace that.

**Hard keywords** (27). These start control flow or literals and are never names:

`and as assert attempt always break continue def elif else false for from if import in is learn none not or pass raise remember return true while`

**Soft keywords at the start of a statement.** Each is a keyword only when followed by a NAME, or by `def` in the case of `gene`. Otherwise it is a name:

`gene fitness module schema` and, for later RFCs, `model agent protocol society app population species pipeline`

So `model = load(...)`, `population(size=64)`, and `agent.send(m)` are ordinary code, while `model pendulum:` starts a declaration. Two names in a row are never a valid expression, so one token of lookahead decides.

**`with` is soft.** It starts a `with` statement only when the logical line has a `:` outside brackets, so `rows |> with(total = _.a + _.b)` still calls a function named `with`.

**Clause keywords** are keywords only inside the block that defines them: `examples holdout score invariant strategy shadow benchmark simulate replay capabilities send reply timeout train evolve on`.

**Reserved for later RFCs** (soft, no effect today): `match case type async await yield`.

### Statements

```text
def NAME(params) [-> Type]: block          # function (one method of a generic function)
gene def NAME(params) [-> Type]: block     # evolvable function (RFC 0003)
fitness NAME: clauses                      # fitness spec for a gene (RFC 0003)
attempt: block (learn [Type as] NAME: block)+ [always: block]
with ITEM [as TARGET], ...: block          # also with (ITEM, ...): over several lines
if / elif / else, for TARGETS in EXPR, while
remember EXPR                              # record a Lesson (RFC 0002)
raise [EXPR [from EXPR]]                   # bare raise re-raises inside learn
assert EXPR [, EXPR]
return, break, continue, pass
TARGETS = EXPR, TARGET: Type [= EXPR], TARGET op= EXPR
import a.b [as c], ... | from a.b import c [as d], ... | from a.b import (c, d,)
@EXPR before def / gene def / module
```

**One statement per line.** `;` is an error with the hint "start a new line". The block after `:` is either an indented suite or a single simple statement on the same line. Lessons, fossils, and mutation diffs all point at lines (RFC 0002, RFC 0003), so one line should hold one thing that can fail.

**`attempt`.**
- The suite runs. On failure, `learn` clauses are matched top to bottom. `learn err:` with no type catches everything, and `learn A | B as err:` catches either type.
- `always` runs on every path.
- `return`, `break`, and `continue` inside `always` are **errors**. Python made them a warning in 3.14 (PEP 765) because they silently discard the failure in flight.
- A `learn` clause **without** `remember` still produces a Lesson with `recorded=false` in debug builds, so the failure is never silently lost (RFC 0002).

**`with`** works as in Python: the context's exit runs on every path and sees the failure, if there was one. The parenthesized form allows a trailing comma and one item per line.

**`raise` and `assert`.**
- `raise E from cause` chains failures, and `raise` alone inside `learn` re-raises.
- `assert` is **never compiled out**: Python's `-O` silently removes checks, which conflicts with fail-closed safety (RFC 0004). A failed `assert` is a failure like any other and becomes a Lesson.

**Assignment.**
- Targets may unpack (`a, b = b, a`) with at most one starred target (`first, *rest = xs`).
- The right side is evaluated first, then targets left to right.
- An annotated assignment has exactly one target.
- An augmented assignment (`+= -= *= /= //= %= ^=`) has one target and never unpacks.

**Imports.**
- `from m import *` is an error with the hint "name what you import". Readers and agents both need to see where every name comes from.
- Relative imports and lazy imports (PEP 810) wait for the module-system RFC.

**Decorators** take any expression (PEP 614), and apply to `def`, `gene def`, `module`, and later declaration blocks.

**Loops have no `else` clause.** Python's `for … else` is widely misread. Use a flag or `any(...)`.

### Functions and parameters

```text
def f(a, b: int = 1, *args, c, d = 2, **kwargs) -> T: ...
```

- Parameters after `*args`, or after a bare `*`, are **keyword-only**, as in Python. Keyword-only parameters do not take part in dispatch (see below). This matches how agents call tools: by name.
- **Defaults are evaluated at every call**, not once at `def` time. This fixes Python's shared-mutable-default pitfall (`def f(xs=[])`).
- In a call, positional arguments and `*splat` come before `name=value` and `**splat`. Giving one parameter twice is an error.
- A generator expression that is the only argument needs no extra parentheses: `sum(x ^ 2 for x in xs)`.

### Expressions and precedence

From lowest to highest:

| Level | Operators | Assoc. |
|---|---|---|
| 1 | `->` (lambda) | right |
| 2 | `x if c else y` | right |
| 3 | `\|>` (pipe) | left |
| 4 | `or` | left |
| 5 | `and` | left |
| 6 | `not` | prefix |
| 7 | `== != < <= > >= in not in is is not` | chained, restricted (below) |
| 8 | `..` `..=` | none |
| 9 | `±` `+/-` | left |
| 10 | `+ -` and `.+ .-` | left |
| 11 | `* / // \ %` and `.* ./ .\` | left |
| 12 | unary `- +` | prefix |
| 13 | `^` and `.^` | **right** |
| 14 | call `f(x)`, broadcast call `f.(x)`, index `a[i]`, attribute `a.b`, string macro | left |

**Comparison chains.**
- `a < b <= c` means `a < b and b <= c`, with `b` evaluated once, as in Python.
- A chain may use only `<`, `<=`, and `==`, or only `>`, `>=`, and `==`. A chain in both directions (`x < y > z`) is an error with the hint to split it.
- `!=`, `in`, `not in`, `is`, and `is not` never chain: `a != b != c` does not mean all three differ, and `x == y in z` misleads. Add parentheses.
- `x is <number or string literal>` is an error with the hint `==`. `is` compares identity, which literals do not have.

**Conditional expression.** `x if c else y` evaluates `c` first, then only one branch. It binds looser than `|>`, so `xs |> mean if xs else 0.0` means `(xs |> mean) if xs else 0.0`.

**Pipe.** `x |> f` is `f(x)`, and `x |> f(a, b)` is `f(x, a, b)`: the left value becomes the **first** argument.

**Placeholder `_`.** Inside a call argument, an expression containing `_` becomes a one-argument lambda, scoped to the **smallest enclosing call argument**. `filter(_.region == "EU")` is `filter(r -> r.region == "EU")`.

**Broadcasting.** A dot before an operator, or before a call's parenthesis, applies it element-wise, with shapes broadcast by RFC 0005.

**Comprehensions** follow Python: `[e for t in it if c]`, `{k: v for …}`, `{e for …}`, and `(e for …)`.
- Several `for` and `if` clauses may follow in order.
- The iterable and the filter are pipe-level expressions, so a conditional expression there needs parentheses, as in Python.
- The loop variables do not leak out of the comprehension.
- `[*xs for xs in groups]` flattens, as in PEP 798 (Python 3.15).

**Starred expressions** unpack in list, set, and tuple displays (`[*a, *b]`), `**` unpacks in dict displays (`{**defaults, **overrides}`), and both unpack in calls.

**Indexing** is 0-based. Slices are half-open (`a[1:3]`), and negative indices count from the end, as in Python.

### Multiple dispatch

All `def`s with the same name visible in a module are **methods of one generic function**.
- A call dispatches on the runtime types of **all** positional arguments and chooses the most specific method.
- Ambiguity is a compile-time error when it can be detected, and otherwise a runtime `AmbiguityError` that is recorded as a Lesson.
- Operators are generic functions too (`+` is `add`), so Peace needs no `__add__`.

### Start rules

| Rule | Input | Used by |
|---|---|---|
| `file` | statements to end of file | `.peace` files |
| `repl` | one statement; a compound statement ends at a blank line | the REPL |
| `eval` | one expression | notebooks, `peace eval`, fitness `score =` expressions |

### Diagnostics

The parser never stops at the first error. It builds a lossless CST with ERROR nodes and keeps going.

Python 3.10 and later show that **hints for likely mistakes** are the cheapest way to teach a language. The grammar marks each one with `# error:`. Every hint in this table needs a test in `tests/syntax/err/`.

| Input | Message |
|---|---|
| `x ** 2` | `**` is not Peace syntax; use `^` for powers |
| `True`, `False`, `None` | Python spelling: use `true`, `false`, `none` |
| `lambda x: …` | Python spelling: use `x -> …` |
| `try:`, `except`, `finally:` | use `attempt:`, `learn`, `always:` |
| `&&`, `\|\|`, `!x` | use `and`, `or`, `not x` |
| `a = 1; b = 2` | one statement per line |
| `"a" "b"` | missing comma, or use `+` |
| `x < y > z`, `a in b in c` | split the chain or add parentheses |
| `x is 7` | use `==`; `is` compares identity |
| `0123`, `.5`, `5.` | write `0o123`, `0.5`, `5.0` |
| `5kg`, `2π` | write `5 kg` (unit) or `2 * π` |
| `a @ b` | `*` is matrix multiply; `.*` is element-wise |
| `from m import *` | name what you import |
| `for … else:` | loops have no `else`; use a flag or `any(...)` |
| `return` inside `always:` | it would discard the failure in flight |
| `function f`, `fn f`, `func f` | use `def` |
| `else if` | use `elif` |
| tab in indentation | indent with spaces |

## Lessons from Python 3.16

Source: the [Python 3.16 language reference](https://docs.python.org/3.16/reference/index.html) (3.16.0a2 docs), including the 3.14 and 3.15 changes it describes.

| Python rule | Peace | Why |
|---|---|---|
| PEG grammar with ordered choice, lookahead, and `s.e+` (PEP 617) | **Adopt** the notation in `spec/grammar.ebnf` | The rules read the same as Python's reference. The parser stays hand-written for lossless trees and error recovery |
| Grammar page generated from the parser's own grammar | **Adapt**: conformance and doc-sample tests | Peace's parser is hand-written, so tests keep the spec and parser from drifting |
| `invalid_*` rules that produce targeted messages | **Adopt** as `# error:` lines plus the Diagnostics table | Good errors are part of the grammar, not an afterthought |
| Soft keywords (`match`, `case`, `type`, `_`, `lazy`) | **Adopt** for all declaration keywords and `with` | `model`, `agent`, `schema`, and `population` are common names in AI code |
| Indentation stack, INDENT/DEDENT | **Adopt** | |
| Tabs expand to multiples of 8, `TabError` | **Decline**: tabs in indentation are an error | One rule instead of two |
| Backslash line joining | **Decline** | `\` is left division. Brackets, trailing operators, and leading `\|>` cover the cases |
| Encoding declaration | **Decline**: UTF-8 only | |
| NFKC identifier normalization | **Adapt**: NFC | NFKC erases distinctions math code needs |
| `_` as wildcard and throwaway | **Adapt**: discard in targets, placeholder in call arguments | |
| `__dunder__` protocol names | **Decline** | Operators are generic functions |
| Unknown escapes kept, with a warning (planned error) | **Adopt the planned end state**: error now | |
| Implicit string concatenation | **Decline** | It hides missing commas |
| f-strings per PEP 701 (nesting, quote reuse, `=`) | **Adopt** | |
| t-strings (PEP 750) | **Adopt** as `t"…"`, and as the input every interpolating string macro receives | Safe prompts and SQL by construction |
| `0123` is an error; `_` between digits | **Adopt** | |
| `.5` and `5.` floats | **Decline** | `.` and `..` are operators in Peace |
| Number followed by a keyword (`1or x`), warning in 3.16 and later an error | **Adopt as an error** for any letter | Units need a space anyway |
| Imaginary literals `1j` | **Defer** to RFC 0005 | |
| Comparison chaining | **Adapt**: one direction only; `in`, `is`, `!=` do not chain | `x < y > z` and `x == y in z` are documented Python traps |
| `x is 7` SyntaxWarning | **Adopt as an error** | |
| Conditional expression | **Adopt**, placed below `\|>` | Pipelines read as the value |
| `:=` assignment expression | **Decline** in Phase 1 | Small gain, contested readability (PEP 572) |
| `lambda` | **Replace** with `->` | |
| `-x ** 2 == -(x ** 2)` | **Adopt** for `^` | Same as math |
| `//` floor division | **Adopt** | Python users type it |
| `@` matrix multiply | **Decline** | `*` and `.*` (RFC 0005) |
| Bitwise operators | **Decline** in Phase 1 | Rare in data and AI code; their tokens have Peace meanings |
| Comprehensions and generator expressions; `*` in comprehensions (PEP 798) | **Adopt** | The most guessable Python construct |
| `*args`, `**kwargs`, keyword-only `*` | **Adopt** | |
| Positional-only `/` | **Defer** | Interacts with dispatch; see unresolved questions |
| Defaults evaluated once at `def` | **Decline**: evaluated per call | A well-known trap |
| Decorators as any expression (PEP 614) | **Adopt** | |
| `try/except/else/finally` | **Replace** with `attempt/learn/always` | Lessons (RFC 0002) |
| `except A, B:` (PEP 758) | **Adapt**: `learn A \| B as err:` | Reuses type-union syntax |
| `except*` groups | **Defer** to the concurrency RFC | |
| `return` in `finally`, a warning (PEP 765) | **Adopt as an error** in `always` | |
| `with` and parenthesized `with` | **Adopt**, as a soft keyword | |
| `raise … from …`, `assert` | **Adopt**; `assert` is never compiled out | Fail closed (RFC 0004) |
| `for … else`, `while … else` | **Decline** | Misread more often than used |
| `;` between statements | **Decline** | One line, one failure location |
| Star imports | **Decline** | |
| Relative and `lazy` imports (PEP 810) | **Defer** to the module-system RFC | |
| `match`/`case` | **Defer** to its own RFC | It needs care: in Python, `case FOO:` captures instead of comparing |
| `async`/`await`, `yield` | **Defer** to the concurrency RFC | Soft keywords mean deferring costs nothing |
| `class`, `type X = …`, `def f[T]` | **Defer** to the types RFC (unresolved question 4) | |
| `global`, `nonlocal`, `del` | **Defer** to the scoping semantics RFC | |
| `{}` is a dict, no empty-set literal | **Adopt** | Guessable, even if irregular |

## Safety and failure modes

| Failure | Guardrail |
|---|---|
| Source that displays differently from how it runs (bidi controls, Trojan Source) | Lexer error, so a human reviewer reads what runs (RFC 0004 human gate) |
| Look-alike identifiers (`a` Latin vs `а` Cyrillic) in evolved or agent-written code | Confusable-identifier lint. Its scope is unresolved question 6. RFC 0004 human gate |
| Injection through interpolated strings in prompts, SQL, and shell | String macros receive templates, never joined strings (RFC 0004 capabilities limit the damage) |
| A check removed by an optimization flag | `assert` is never compiled out; safety code fails closed (RFC 0004) |
| A failure silently swallowed by `return` in `always` | Parse error |
| Parse errors | Error-tolerant parser; each error has a fix hint; the REPL records it as a Lesson (`peace lessons --mine`) |
| Mutations producing unreadable or invalid code | Mutations operate on the CST, never on text, so a variant always round-trips to valid, formatted source |

## Drawbacks

- `true/false/none`, `^`, and the comparison-chain limits break Python muscle memory. The parser recognizes the Python spellings and gives a one-line hint for each.
- Soft keywords make tools such as syntax highlighters and simple tokenizers context-sensitive, as Python found with `match`. Peace limits this to one rule: a statement-start keyword followed by a NAME.
- `_` placeholder scoping is a classic source of confusion (Scala). The "smallest enclosing call argument" rule is simple but must be taught early.
- Evaluating defaults per call costs time when a default is expensive. Hoist the value to a module-level constant.

## Alternatives

- **Python-exact syntax** (`**`, `True`, `lambda`, bitwise operators): the most familiar, but it clashes with Julia-style math and the pipeline style used across the docs.
- **Braces instead of indentation:** easier to parse, but it abandons the Python heritage.
- **All declaration keywords hard:** simpler tokenizing, but it broke real samples (`model`, `population(...)`, `with(...)`) during prototyping.
- **NFKC like Python:** compatible with Python's identifier rules, but it folds `ℝ` into `R` and `x²` into `x2`.

## Prior art

Python (indentation, f-strings and t-strings, comprehensions, soft keywords, PEG grammar notation, chained comparisons), Julia (broadcast dots, `^`, symbols, non-standard string literals, NFC with custom equivalences), Elixir and F# (`|>`), Scala (`_` placeholder), Rust (`..` and `..=` ranges, bidi-control lints).

## Unresolved questions

1. Should `..` in a `for` header and `..` in an evolvable range (`~x in a..b`, closed) use one notation? Proposal on the table: ranges are always half-open, and evolvable ranges use `a..=b`.
2. Unit suffix parsing: is `5 m` (space-separated) unambiguous enough, or do we require a marker (`5[m]`)? The number-then-letter error makes `5m` unavailable either way.
3. Is the symbol-wins rule for `xs[:n]` acceptable to Python users, or should symbols in index position need a different spelling?
4. `class` vs. `struct` vs. `schema`: which record types exist in Phase 1? Leaning: `schema` for validated data records, `struct` for plain records, no inheritance. The types RFC also owns `def f[T]` and `type X = …`.
5. Positional-only parameters (`/`): needed for dispatch-only methods, or do keyword-only parameters suffice?
6. Confusables: lint on mixed-script identifiers only (as Rust does), or on any identifier that is confusable with another name in scope? Owner: the `peace-syntax` maintainers.
7. Should leaving a `with` block because of a failure record a Lesson on its own, or only through `learn`/`remember`? Owner: RFC 0002.

## Test plan

- **Conformance corpus** in `tests/syntax/ok/`, one `.peace` file per construct, plus every `peace` block from `README.md`, `docs/`, and `rfcs/`, parsed in CI. Blocks that use syntax not yet specified or implemented are listed in `tests/syntax/docs-allowlist.txt` with a reason, and must keep failing until they parse.
- **Round-trip:** `parse → CST → print` reproduces the input byte for byte, for every file and every prefix of every corpus file.
- **Diagnostics:** one file in `tests/syntax/err/` per row of the Diagnostics table, asserting the message and its position.
- **Lexical edge cases:** BOM at offset 0 and elsewhere, lone CR, bidi controls in code, strings, and comments, NFC-equal identifiers resolving to one name, `x²` lexing as two tokens, and number-then-letter errors.
- **Precedence:** S-expression tests for every level of the table, including `-x ^ 2`, `2 ^ -1`, conditional vs. pipe, and every legal and illegal comparison chain.

## History

- **Revision 1** (2026-11-21): first draft.
- **Revision 2** (2026-11-21): changes after a review against the Python 3.16 reference:
  - soft keywords;
  - `with`, `raise`, and `assert`;
  - comprehensions and conditional expressions;
  - starred unpacking and keyword-only parameters;
  - per-call defaults;
  - `//`;
  - restricted comparison chains;
  - stricter literals;
  - bidi controls and NFC;
  - the diagnostics table;
  - start rules;
  - a PEG-style grammar.
