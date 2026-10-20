# Exercise: Complete the incremental pipeline (90 minutes)

Use your AI assistant however you like. We want to see how you work with it. Ask us questions whenever the spec is unclear.

## Context

A pipeline copies events from a source system into a warehouse table incrementally. The warehouse here is SQLite so everything runs locally; treat it as you would a real warehouse.

```
source.fetch(updated_after) -> clean -> dedupe -> data-quality check -> load into fact_events -> advance watermark
```

| File | State |
|---|---|
| `pipeline/source.py` | Done. `FakeSource.fetch(updated_after)` returns rows with `updated_at` after the given timestamp |
| `pipeline/warehouse.py` | Done. Schema for `fact_events`, `pipeline_state`, `dq_failures` |
| `pipeline/state.py` | Done. `StateStore` reads and writes the watermark. It does **not** commit; the caller does |
| `pipeline/transform.py` | Done. `clean()` rejects invalid rows. `dedupe_latest()` keeps one row per `id` |
| `pipeline/quality.py` | **Incomplete.** `check_batch()` |
| `pipeline/runner.py` | **Incomplete.** `load()` and `run_incremental()` |

Timestamps are ISO 8601 strings without a timezone (`2024-01-01T10:00:00`) and compare correctly as strings. Read the existing code first, then run `pytest`.

## Requirements

### Part 1: data quality (about 10 minutes)

`check_batch(total, rejected)` raises `DataQualityError` when more than `MAX_REJECT_RATE` of a non-empty batch was rejected by `clean()`.

### Part 2: load (about 20 minutes)

`load(conn, rows)` upserts rows into `fact_events` by `id` and returns the number of rows written.

- It must be **idempotent**: running the same load twice leaves the same data.
- An **older version must never overwrite a newer one**. Compare `updated_at`.
- It must **not commit**. The caller controls the transaction.

### Part 3: the run (about 30 minutes)

`run_incremental(source, conn, name="events", lookback_minutes=60, now=None)` runs one incremental load and returns a `RunResult`.

1. Read the watermark. Extract rows with `updated_at` after `watermark - lookback_minutes`. The lookback catches **late-arriving** rows, whose `updated_at` is slightly behind the watermark. On the very first run (watermark at `EPOCH`) extract everything.
2. `clean()` the rows. Write each rejected row to `dq_failures` (`rule` = the rejection reason, `detail` = the row id).
3. Call `check_batch`. If it raises, record the failure in `dq_failures`, commit that, and re-raise. Nothing is loaded and the watermark does not move.
4. Deduplicate, then `load`.
5. Advance the watermark to the largest `updated_at` seen in the extract (never backwards), **in the same transaction as the load**. Commit once. If anything fails, roll back so neither the data nor the watermark changes.
6. An empty extract leaves everything unchanged.

## Part 4: tests (about 20 minutes)

Add tests for behaviour the existing tests do not cover. Focus on what is most likely to corrupt data in production.

## Part 5: walk us through it (about 10 minutes)

Be ready to explain your design, anything in the spec you had to interpret, and what you would add before running this on real data.
