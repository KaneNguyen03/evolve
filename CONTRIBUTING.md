# 🤝 Contributing to Evolve

Thank you for wanting to help Evolve grow! 🌱 Evolve is in its **Seed** phase: there's no compiler yet, so the most valuable contributions are **ideas, critiques, and real-world failure stories**.

> In the spirit of the language: your rough, imperfect idea is welcome. We'd rather evolve it together than never see it. 🍂→🌿

---

## 🌱 Ways to contribute right now

| | Contribution | How |
|:---:|---|---|
| 💡 | **Language idea or design change** | Open an [RFC issue](https://github.com/peace-program-project/peace/issues/new?template=rfc.yml) |
| 🧪 | **A real-world failure for EvoBench** | Open a [EvoBench case](https://github.com/peace-program-project/peace/issues/new?template=evobench.yml) |
| 🌍 | **A use case or application** | Open a [Use case issue](https://github.com/peace-program-project/peace/issues/new?template=use-case.yml) |
| 📝 | **Docs fixes** | Open a pull request directly |
| ❓ | **Questions and open-ended discussion** | Use [Discussions](https://github.com/peace-program-project/peace/discussions) |

---

## 📜 The RFC process

Any change to the **language, Lesson or lineage formats, or safety model** goes through an RFC.

1. 💬 **Discuss**: open an RFC issue with the problem, the proposal, and what could go wrong.
2. 📄 **Draft**: once there's interest, open a PR adding `rfcs/NNNN-short-name.md`.
3. 🔍 **Review**: at least one core maintainer and a two-week comment period.
4. ✅ **Decide**: accepted, postponed, or declined, always with a written rationale. Declined RFCs are kept too. In Evolve, failures are fossils, not trash. 🦴

---

## 🧪 EvoBench cases

EvoBench is a public benchmark of **real software failures caused by a changing environment**. A good case has:

- a small program that used to work,
- the environment change that broke it (schema drift, API change, new locale, dependency upgrade…),
- a few input → expected output examples,
- **invariants** that a correct fix must never violate.

> [!WARNING]
> **Anonymize everything.** Never include personal data, secrets, customer names, or proprietary code.

---

## 🛠️ Code contributions (from Phase 1)

When code lands, Evolve will be a Rust workspace on the **beta** toolchain (see [`rust-toolchain.toml`](rust-toolchain.toml)).

- `cargo fmt` and `cargo clippy -- -D warnings` must pass.
- Code must also compile on **stable** (CI checks both).
- Add tests. For anything in `evo-search`, add a **fitness** test too. 🎯
- Keep PRs small and focused, and link the related issue or RFC.

---

## 🎨 Style

- Follow the [brand guide](docs/brand.md) for tone: calm, precise, and humble.
- Code samples in docs use the `evo` code fence.
- Prefer clear words over clever ones. *Readable is better than clever.* 🧘

---

## 🕊️ Code of Conduct

Everyone participating in Evolve agrees to our [Code of Conduct](CODE_OF_CONDUCT.md). Be kind. Failure is how we all learn.

---

## 📄 License

Evolve is licensed under the [Apache License, Version 2.0](LICENSE). By contributing, you agree that your contributions are licensed under Apache-2.0, as described in Section 5 of the license.
