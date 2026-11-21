---
rfc: 0002
title: Lesson schema and fossil record
status: draft
authors: [peace-program-project]
created: 2026-11-21
phase: Seed → Sprout
requires: [0001]
spec: [spec/lesson.schema.json]
---

# RFC 0002: Lesson schema and fossil record

## Summary

A **Lesson** is the structured record of one failure. The **fossil record** is the append-only store of all Lessons and lineage events for a project. This RFC defines the Lesson fields, the storage layout, privacy rules, and the query surface. It's the first thing the Phase 1 engine (`evo-fossil`) builds, and it's shared by the Evolve language and the Python engine.

## Motivation

Every promise Evolve makes (agents that learn, self-healing pipelines, regression evals from production) depends on failures being **data with a stable shape**. If Lessons are just log lines, none of it works. This schema is frozen at v0 at the end of Phase 0 so that both tracks build on it.

## Guide-level explanation

```evo
attempt:
    order = parse_order(row)
learn ParseError as err:
    remember err                           # writes one Lesson
    quarantine(row)

evo.fossils()
  |> filter(_.gene == "parse_order" and _.origin == :prod)
  |> groupby(:kind)
  |> count()
```

```bash
evo lessons --gene parse_order --since 7d
evo lessons show 01JD3Q8K6Z9X2V4M7N5B1C0A8E
```

## Reference-level explanation

### Lesson v0 fields

The normative definition is [`spec/lesson.schema.json`](../spec/lesson.schema.json). Summary:

| Field | Type | Required | Meaning |
|---|---|:---:|---|
| `schema` | `"evo.lesson/v0"` | ✅ | Format version |
| `id` | ULID string | ✅ | Unique, time-sortable id |
| `time` | RFC 3339 timestamp (UTC) | ✅ | When the failure happened |
| `project` | string | ✅ | Project name from `evo.toml` (or Python package) |
| `origin` | `dev` \| `test` \| `ci` \| `staging` \| `prod` \| `sandbox` | ✅ | Where it happened |
| `kind` | string | ✅ | Error type path, e.g. `std.parse.ParseError` |
| `message` | string | ✅ | Human-readable message, **after redaction** |
| `site` | object | ✅ | `module`, `function`, `gene` (if any), `variant` (if any), `file`, `line`, `col` |
| `stack` | array of frames | | Frames as `{module, function, file, line}`; no local variable values |
| `inputs` | array of input records | | Each argument as `{name, type, fingerprint, sample?}`, see Privacy |
| `env` | object | | `evo_version`, `os`, `arch`, dependency versions, capabilities granted |
| `recorded` | bool | ✅ | `true` if `remember` was called; `false` for implicit debug Lessons |
| `severity` | `info` \| `warn` \| `error` \| `fatal` | ✅ | |
| `tags` | array of strings | | Free-form labels |
| `parent` | Lesson id | | A Lesson that caused this one (error chains) |
| `resolution` | object | | Filled in later: `{variant, promoted_at, fitness_delta, by}` |
| `redaction` | object | ✅ | `{policy, fields_redacted}`: which policy ran and what it removed |

### Lineage events

The same store holds **lineage events**, one per state change of a variant (RFC 0003/0004): `proposed`, `evaluated`, `approved`, `promoted`, `reverted`, `extinct`, with `{gene, variant, parent_variants, source_hash, fitness, actor}`. Lessons point at variants and variants point back at the Lessons that motivated them.

### Storage layout

```
.evo/
├── fossils/
│   ├── lessons/date=2026-11-21/part-0000.parquet   # append-only, partitioned by day
│   └── lineage/date=2026-11-21/part-0000.parquet
├── index.sqlite                                   # ids, gene, kind, origin, time → file + row
└── config.toml                                    # retention, redaction policy
```

- **Append-only.** Records are never edited. A `resolution` update is a new lineage event that the query layer joins in.
- **Write path:** buffered in memory, flushed on size (1 MiB), time (5 s), or process exit. A crash may lose the last buffer, never corrupt earlier files.
- **Export:** `evo lessons export --format jsonl|parquet`.

### Privacy and redaction (on by default)

1. **Inputs are fingerprinted, not stored.** Each input is stored as `{type, fingerprint}` where the fingerprint is a keyed hash (per-project secret) of a canonical encoding. That's enough to deduplicate and to tell whether two failures had the same input, without keeping the value.
2. **Samples are opt-in.** `@lesson(sample=true)` on a gene, or `remember err with sample` in code, stores a **redacted** sample: strings pass through the PII redactor (emails, phone numbers, card numbers, IBANs, national IDs, names in known fields), and values over 4 KiB are truncated.
3. **Messages are redacted** with the same redactor before storage.
4. **Retention:** default 90 days for `prod` Lessons, unlimited for others; configurable.
5. **Never leaves the machine** unless the user runs an explicit export or opts in to a shared registry (future).

## Safety and failure modes

- A Lesson write must **never** fail the program. If the store is unavailable, Lessons go to a bounded in-memory ring and a warning is printed once.
- Lesson volume is rate-limited per `(kind, site)`: after 100 identical Lessons per minute, further ones are counted, not stored.
- Agents read Lessons through the MCP server with the same redaction applied. Raw samples are never exposed over MCP.

## Drawbacks

- Fingerprints without values limit what an agent can learn from a single Lesson. Mitigation: opt-in samples for genes where data is not sensitive.
- Parquet plus SQLite is two formats. It keeps queries fast and files portable, at the cost of an index that can drift. `evo fossils reindex` rebuilds it.

## Alternatives

- **Plain JSONL logs:** simplest, but slow to query at scale and weakly typed.
- **An embedded database only (SQLite):** easy queries, but poor for analytics and harder to share as files.
- **OpenTelemetry events:** good transport for later, but no schema for evolution data. A future exporter can map Lessons to OTel.

## Prior art

Sentry and similar error trackers (grouping by fingerprint), OpenTelemetry (structured events), Arrow/Parquet data lakes, Erlang/OTP supervision trees (failure as a normal event).

## Unresolved questions

1. Is a per-project keyed hash enough for fingerprints, or do we need per-gene keys so that fingerprints can't be correlated across genes?
2. Which PII detectors ship in v0, and is the default policy locale-aware?
3. Should `sandbox` Lessons (failures of candidate variants) live in the same store or a separate one that's cleaned up aggressively?

## Test plan

- JSON Schema validation for every Lesson written in tests.
- Property tests: write N Lessons, crash at a random point, reopen; every flushed Lesson is readable and the index matches.
- Redaction tests with a corpus of synthetic PII in messages and samples.
- Python engine and Evolve runtime write Lessons that the other can read (cross-track conformance).
