---
name: evo-implement
description: Implement Evolve roadmap work in the Rust workspace (beta toolchain) or the Python engine, driven by an RFC. Use for "implement", "start coding Evolve", "build evo-syntax / evo-fossil", "add a crate", or any code change to the Evolve compiler, runtime, or engine.
---

# Evolve implement

## 1. Find the contract

Name the roadmap item (`docs/roadmap.md`) and the RFC that governs it (`rfcs/`). No RFC: stop and offer the `evo-rfc` skill. A `draft` RFC is fine for a prototype; say so in the commit message.

## 2. Workspace

- Toolchain: `rust-toolchain.toml` pins `beta`. If `cargo` says it's missing, run `rustup toolchain install beta`.
- If there's no root `Cargo.toml`, create a workspace (`edition = "2024"`, members under `crates/`). Add only the crates the task needs, named `evo-*` as in the README's crate layout.
- Python engine code lives in `engine/python/` (PyO3 bindings arrive later; plain Python prototypes are fine in Phase 1).

## 3. Tests first

Turn the RFC's test plan into failing tests before writing the code: conformance files in `tests/`, round-trip tests for syntax, JSON Schema validation against `spec/lesson.schema.json` for anything that writes Lessons.

## 4. Build the smallest slice that passes

Rules that come from the RFCs and must hold in code:
- Lesson writes never fail the program (RFC 0002).
- Operators never see holdout data and never write fossils directly (RFC 0003).
- Capabilities default to none; gates come from `evo.toml`, not source; failures in safety code fail closed (RFC 0004).
- No nightly-only features. Every `unsafe` block has a `// SAFETY:` comment.

## 5. Verify

```bash
cargo fmt --all --check
cargo clippy --all-targets -- -D warnings
cargo test
cargo +stable test        # code must also build on stable
```

For engine or bench work, also run `python3 bench/run.py bench/cases/0001-date-format-drift`.

## 6. Close the loop

Update the RFC (`status: implemented` only when the user agrees), tick the roadmap item, and report what ran, with its output.
