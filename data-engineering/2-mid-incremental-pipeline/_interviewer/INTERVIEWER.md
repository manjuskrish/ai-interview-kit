# Interviewer guide: Data Engineering, Mid/Senior (Incremental pipeline)

**Time:** 90 minutes. **Tests:** idempotent loads, watermarking, late-arriving data, transactional correctness, data-quality gates, spotting a latent bug in existing code.
**Most weighted:** Verification (25%), Prompt and context (20%), Design judgment (15%).

## Setup (3 minutes)

Candidate runs `pytest`. All five pipeline tests fail with `NotImplementedError`. `check_batch`, `load` and `run_incremental` are stubs.

## Seeded issues and intentional ambiguity

| Issue | Where | Notes |
|---|---|---|
| **Latent bug:** `dedupe_latest()` compares `event_ts`, not `updated_at`, and on a tie keeps the *first* row | `pipeline/transform.py` | A correction (same `id`, same `event_ts`, newer `updated_at`) loses to the original. No visible test covers it; the hidden test does. An AI building on the existing code will not notice |
| Watermark before commit | `CANDIDATE.md` Part 3 | The spec requires the watermark and load in one transaction. AI often calls `set_watermark` then `commit` separately, or commits inside `load` |
| `load()` must not commit | `CANDIDATE.md` Part 2 | AI often commits in `load` (breaks rollback) |
| Stale overwrite | `load()` | A naive `INSERT OR REPLACE` lets an older version clobber a newer one after a lookback re-fetch |
| Rejected rows and the watermark | `CANDIDATE.md` Part 3 | The watermark advances past rejected rows (they are quarantined). A strong candidate notes the tradeoff and asks |
| Boundary of the reject-rate check | `CANDIDATE.md` Part 1 | "More than 20%". Exactly 20% passes. The hidden tests avoid the boundary |
| Strict `>` in `fetch` | `source.py` | A row with `updated_at` equal to the watermark minus lookback is excluded. A strong candidate notices that identical timestamps can be missed |

## AI traps to watch for

- Advancing the watermark inside `load()` or before the load is committed.
- `INSERT OR REPLACE` or a plain `INSERT` followed by a catch of `IntegrityError`.
- A try/except that logs and carries on, leaving a half-applied run.
- Using wall-clock `now()` as the new watermark instead of the max `updated_at` seen.
- Tests that mock the source and the database, so no real SQL ever runs.
- Trusting `transform.py` without reading it.
- Computing the lookback in a way that fails on the first run (watermark `EPOCH`).

## Mid-session change (at about 55 minutes)

Say: "The source team tells us rows can also be deleted, and they send a `deleted: true` flag with a newer `updated_at`. How do you handle that?" Watch whether they treat it as an upsert of a tombstone versus a hard delete, whether `load` stays idempotent, and whether they update tests first.

## Probing questions

1. What happens if the process dies between `load` and `set_watermark`?
2. Why is a lookback window needed? What does it cost?
3. What breaks if two runs overlap?
4. How would you backfill the last 30 days without disturbing the watermark?
5. What would you monitor in production?
6. How do you know the table matches the source?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Prompt and context | Pastes the stubs and the error | Points the AI at the existing modules, the transaction rule and the idempotency requirement | Tells the AI the invariants first (never commit in `load`, watermark moves only with the data) |
| Verification | Runs the given tests | Adds tests for stale overwrite, correction within a batch, rollback on failure | Finds the `dedupe_latest` bug without being asked; tests tie timestamps and empty batches |
| Design judgment | Implements what the spec says | Explains the transaction boundary and the lookback tradeoff | Raises keyset pagination, tombstones, backfills and monitoring unprompted |
| Ownership | Explains the happy path | Explains each failure mode and what state it leaves behind | Describes how to detect drift between source and warehouse |

## Reference materials

- `_interviewer/solution/` is a complete implementation (it also fixes `transform.py`).
- `_interviewer/hidden_tests/test_hidden.py` covers corrections, stale overwrites, rollback and quarantined rows. Run it after the session.
