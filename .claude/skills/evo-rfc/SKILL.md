---
name: evo-rfc
description: Draft, revise, or review an Evolve RFC in rfcs/ and the spec files it owns (spec/grammar.ebnf, spec/lesson.schema.json). Use for "write an RFC", "spec this Evolve feature", "review RFC 0003", "update the Evolve grammar", or graduating a brainstorm idea.
---

# Evolve RFC

RFCs decide anything that changes the language, its file formats, or its safety model. Process and statuses: `rfcs/README.md`.

## Draft or revise

1. Take the next free number from the index in `rfcs/README.md`. Copy `rfcs/0000-template.md` to `rfcs/NNNN-short-name.md`.
2. Fill every section. "Unresolved questions" and "Test plan" are never empty.
3. **Code samples must parse** under RFC 0001 and `spec/grammar.ebnf`. If the RFC needs new syntax, change the grammar in the same edit and list it under `spec:` in the front matter.
4. The safety section names the RFC 0004 guardrail that handles each failure mode.
5. Set `requires:` to every RFC whose rules it relies on. Check for conflicts by searching `rfcs/` for the keywords and constructs it touches.
6. Add or update the row in the `rfcs/README.md` index. If the idea came from `brainstorm/`, set that idea's status to 📜 rfc with a link.

## Review

Report findings, most serious first:
- Motivation tied to a use case or mission in `docs/`?
- Reference section precise enough to write the tests in its test plan?
- Conflicts with other RFCs, the grammar, or the Lesson schema?
- Every failure mode mapped to a guardrail?
- Unresolved questions concrete and owned?

## Status

Change `status:` only when the user decides it. Never mark an RFC `accepted` on your own.
