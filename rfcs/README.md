# 📜 Evolve RFCs

RFCs ("requests for comments") are how Evolve decides anything that changes the **language, its file formats, or its safety model**. Code follows RFCs, not the other way around.

## Status values

| Status | Meaning |
|---|---|
| 🌱 `draft` | Being written; open for early comments |
| 💬 `review` | Complete and in its comment period (at least 2 weeks) |
| ✅ `accepted` | Approved; implementation may start |
| 🛠️ `implemented` | Shipped; the RFC records what was built |
| ⏸️ `postponed` | Good idea, wrong time |
| 🦴 `declined` | Not doing it. Kept as a fossil, with the reason |
| 🔁 `superseded` | Replaced by a later RFC (linked) |

## Process

1. 💬 Open an issue with the [RFC form](https://github.com/peace-program-project/peace/issues/new?template=rfc.yml) to test the idea.
2. 📄 Copy [`0000-template.md`](0000-template.md) to `NNNN-short-name.md` (next free number) and open a PR.
3. 🔍 Comment period: at least two weeks, at least one core maintainer review.
4. ✅ Decision recorded in the RFC header with a short rationale. Declined RFCs stay in the repo.

Machine-readable artifacts that an RFC defines (grammars, schemas) live in [`../spec/`](../spec/) and are versioned with the RFC.

## Index

| RFC | Title | Status | Phase |
|---|---|---|---|
| [0001](0001-syntax-core.md) | Core syntax | 🌱 draft | Seed → Sprout |
| [0002](0002-lesson-schema.md) | Lesson schema and fossil record | 🌱 draft | Seed → Sprout |
| [0003](0003-gene-fitness-semantics.md) | `gene`, `fitness`, and selection semantics | 🌱 draft | Sprout → Branch |
| [0004](0004-promotion-and-safety.md) | Promotion and safety model | 🌱 draft | Branch → Bloom |
| [0005](0005-data-model.md) | Data model: arrays, frames, units, uncertainty | 🌱 draft | Root |
