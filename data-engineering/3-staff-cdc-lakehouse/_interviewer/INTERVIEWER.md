# Interviewer guide: Data Engineering, Staff+ (CDC into a lakehouse)

**Time:** 120 minutes. **Tests:** scoping, correctness under duplicates, disorder and deletes, schema evolution, backfills, SLAs, monitoring, cost, judgment about what not to build.
**Most weighted:** Design judgment (30%), Decomposition (20%), Ownership (15%).

You play the data platform owner (call yourself "Priya"). Answer like a busy owner: short and honest, vague until pushed. Reveal hidden facts only when asked something that gets near them.

## Stakeholder script

| If they ask about... | Priya says |
|---|---|
| The table | `orders`: about 2 billion rows, growing 5 million a day. Peak 8,000 changes/sec after promotions |
| Consumers | Finance (daily reports), analytics (dashboards), ML (features). Nobody agrees on what "current" means yet |
| Freshness | Dashboards want the current-state table within 5 minutes. Finance can wait until 06:00 |
| History | Finance needs full history for audit, kept 7 years. They want "state as of any date" |
| Deletes | Hard deletes happen. Deleted orders must disappear from the current-state table. History keeps them |
| Ordering | Per-order ordering matters. The bus guarantees order per key within a partition, but not across restarts |
| Duplicates | The bus is at-least-once. Duplicates happen, especially after consumer restarts |
| Schema | Columns are added roughly weekly. Renames and type changes are rare but happen |
| Initial load | There is a full snapshot (the `op: "r"` events). It takes about 6 hours to produce |
| Tooling | Kafka with Debezium, S3, and Spark/Glue are available. A table format (Iceberg or Delta) is approved but nobody has run it at this scale |
| Correctness | "The lakehouse must match the source." Push them to define how that is measured |
| Cost | Do not volunteer a number. Ask them to estimate and justify |
| Team | 3 data engineers. On-call is shared with the platform team |

## Hidden facts (reveal only if asked)

- Late events can arrive up to 2 hours after the change.
- After a source failover the `lsn` can reset, so `lsn` alone is not a global ordering. `ts_ms` is not strictly monotonic either.
- Some columns are PII (the customer ID mapping). GDPR deletions must reach history within 24 hours.
- Debezium sends tombstone messages (null value) after deletes, and these are not in the sample file.
- One team reads the raw landing zone directly and would break if you change its layout.

## Mid-session changes

Introduce in order, about 75–90 minutes in:

1. "The orders team is renaming `amount` to `amount_cents` next week and changing it to an integer. What happens to your pipeline?"
2. "We found a bug that corrupted the last 90 days of `status` values in the source. They've fixed it. How do you rebuild the lakehouse?"
3. (If time) "Legal says a GDPR deletion must also erase the customer from history within 24 hours. Does your design allow it?"

## What to look for

**Scoping**
- Asks about consumers, freshness, history needs, deletes, delivery guarantees, volume, schema change rates, existing tooling.
- Separates the current-state table from the history, and decides what each needs.
- Proposes a narrow v1 and says what is deferred.

**Correctness**
- Idempotent apply keyed on the primary key, with a defined ordering rule (source position, with a tiebreak) and a plan for when `lsn` resets.
- Duplicates (lsn 1009 in the sample), out-of-order events (1011 before 1010), delete followed by re-insert (id 3), and deletes of rows that never arrived.
- Does not let an older event overwrite a newer one.
- Handles snapshot (`r`) events interleaved with live changes.

**Design**
- Landing zone of raw immutable events, then a merge into current state. Replay and backfill come from the raw log.
- Merge strategy at scale (batch micro-merge, partition pruning, compaction) with cost in mind.
- Schema evolution: additive columns, the rename and type change, a contract with the source team, and what breaks downstream.
- Late data window and its effect on freshness.
- Monitoring: freshness lag, volume, duplicates rate, row-count reconciliation against the source, schema-drift alerts.
- Runbook for stuck consumers, poison events and replays.

**AI use**
- Uses AI to scaffold the merge logic and tests, then checks it against the messy sample (duplicates, disorder, delete and re-insert).
- Notices when the AI hard-codes the sample's columns or ignores deletes.
- Challenges AI suggestions that over-build (streaming frameworks where a batch merge fits).

## Red flags

- Starts building before asking a single question.
- Chooses tools (Flink, Spark, Iceberg) before requirements.
- Treats updates as inserts, or drops deletes.
- Orders events by arrival, or by `ts_ms` alone, with no discussion.
- No story for backfill or reprocessing.
- No answer to "how do you know it matches the source?".
- Cannot explain code the AI generated.

## Probing questions

1. Walk me through what happens to id 3 in the sample file.
2. What happens when the same event arrives twice, a week apart?
3. How would you detect that the lakehouse has silently drifted from the source?
4. What does a replay cost, and how long does it take?
5. What breaks when the source adds a column? When it renames one?
6. What would you cut if you only had two weeks?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Decomposition | Reads the file and writes a table | Separates raw landing, current state and history, with a replay path | Sequences the build so a correct current-state table ships first and risks are retired early |
| Design judgment | Follows the brief | Surfaces ordering, deletes, schema change and backfill, and picks an approach with reasons | Handles the rename, the 90-day rebuild and the GDPR change without a redesign; puts numbers on cost and freshness |
| Verification | Eyeballs the output on the sample | Tests duplicates, out-of-order events, delete and re-insert | Reconciliation checks against the source, property-style tests on the generated feed, drift alerts |
| Ownership | Explains the demo | Explains every decision and gap | Gives a runbook, on-call plan and rollout with kill criteria |
