# 🔒 Security Policy

Peace is designed around **safe self-modification**: sandboxed mutations, capabilities, `@conserved` code, budgets, and human promotion gates. We take weaknesses in that model seriously, even at the design stage.

## 📮 Reporting a vulnerability

Please **do not open a public issue**. Instead, use GitHub's private reporting:

➡️ **[Report a vulnerability](https://github.com/peace-program-project/peace/security/advisories/new)**

Please include what you found, how to reproduce it (or why the design allows it), and its potential impact. We'll acknowledge your report within a few days.

## 🎯 What's in scope

- **Design flaws** in the safety model (for example, a way for a mutation to escape the sandbox, bypass a promotion gate, or alter `@conserved` code)
- Weaknesses in the Lesson format that could leak personal data
- Once code exists: vulnerabilities in the compiler, runtime, sandbox, or MCP server

## 🗓️ Supported versions

Peace has no releases yet. This policy will list supported versions starting with `v0.1`.
