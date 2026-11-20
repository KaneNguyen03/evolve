---
name: peace-brainstorm
description: Brainstorm Peace language ideas (features, syntax, use cases, AI missions) and record them in brainstorm/. Use for "brainstorm Peace", "what if Peace had X", "explore an idea for Peace", or deciding an open question before writing an RFC.
---

# Peace brainstorm

Turn a topic into options, a recommendation, and a written record. This skill writes only to `brainstorm/`. It never edits RFCs or docs.

## 1. Load what's already decided

Read `rfcs/README.md` (index), the newest files in `brainstorm/`, and the "Open questions" section of `README.md`. If the topic is already settled by an RFC, say so, link it, and brainstorm only what's still open.

## 2. Diverge

Generate 5 to 8 options, from conservative to radical. For each:
- a one-line `peace` code sketch,
- who benefits (persona, or use case number from `docs/use-cases.md`),
- how fitness or success would be measured,
- what fails or gets abused, and which guardrail from RFC 0004 catches it.

## 3. Converge

Score each option on value, feasibility (the roadmap phase that could ship it), and safety risk. Recommend one or two, with the reason in one sentence each. Ideas that conflict with the Zen of Peace (README) are dropped, with the conflict named.

## 4. Record

Write `brainstorm/YYYY-MM-DD-<topic>.md` with a table of ideas and statuses (🌱 seed, 🌿 growing, 📜 rfc, 🦴 fossil). Dropped ideas stay, with why. Add a row to the index in `brainstorm/README.md`.

## 5. Hand off

Offer to turn the top idea into an RFC with the `peace-rfc` skill. Don't start the RFC without a yes.
