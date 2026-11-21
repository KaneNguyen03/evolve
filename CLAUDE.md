# Peace: project guide for Claude

Peace is a programming language in which a program's failures make it better instead of only breaking it: Python-readable, Julia data-native, built on Rust (beta channel). Its missions are next-gen AI models, AI-native apps, and agent-to-agent systems. Status: **Seed phase**: design docs, draft RFCs, and a first crate (`peace-syntax`, the parser prototype).

## Where things are

| Path | What |
|---|---|
| `README.md`, `docs/vision.md`, `docs/use-cases.md`, `docs/roadmap.md` | Vision, missions, use cases, phased plan |
| `rfcs/` | Design decisions. `rfcs/README.md` has the process and index |
| `spec/` | Machine-readable specs owned by RFCs: `grammar.ebnf` (RFC 0001), `lesson.schema.json` (RFC 0002) |
| `crates/peace-syntax/` | Lexer + lossless rowan CST parser for RFC 0001 |
| `tests/syntax/` | Parser corpus: `ok/` must parse cleanly, `err/` must report errors, `docs-allowlist.txt` lists doc samples waiting on RFCs |
| `bench/` | PeaceBench cases and the reference scorer `bench/run.py` |
| `brainstorm/` | Dated idea logs before they become RFCs |
| `assets/`, `tools/brand/generate.py`, `docs/brand.md` | Brand assets; regenerate SVGs with the script, never hand-edit them |

## Rules

- **RFC first.** Changes to the language, file formats, or safety model need an RFC in `rfcs/`. Code follows RFCs.
- **Samples must parse.** Every `peace` code block in docs and RFCs must follow RFC 0001 and `spec/grammar.ebnf`. If a sample needs new syntax, change the grammar through an RFC.
- **Safety defaults** (RFC 0004): capabilities default to none, promotion is human-gated, safety machinery fails closed. Never write docs or code that weaken these defaults without an RFC.
- **Rust:** beta toolchain from `rust-toolchain.toml`, edition 2024, crates named `peace-*`. Code must also build on stable. No nightly-only features.
- **Docs voice:** calm, precise, humble (`docs/brand.md`). Use the `peace` code fence. Emojis follow the brand guide's emoji vocabulary.
- **License:** Apache-2.0. New files need no per-file header.

## Commands

```bash
cargo test                                                   # unit, corpus, round-trip, and doc-sample tests
cargo run -p peace-syntax --example dump -- file.peace       # print a file's syntax tree and errors
python3 bench/run.py bench/cases/0001-date-format-drift      # score a PeaceBench case (exit 1 = not healed)
python3 tools/brand/generate.py assets                       # regenerate brand SVGs
```

## Project skills (`.claude/skills/`)

| Skill | Use it to |
|---|---|
| `peace-brainstorm` | Explore an idea or open question and record it in `brainstorm/` |
| `peace-rfc` | Draft, revise, or review an RFC and the spec files it owns |
| `peace-implement` | Implement roadmap work in Rust or the Python engine from an RFC |
| `peace-bench` | Author a PeaceBench case, or heal and score one |

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. Route only to skills in the session's available-skills list; answer directly for quick questions or small scoped edits.
