# Interviewer guide: Cloud SWE, Staff+ (Multi-tenant ingestion platform)

**Time:** 120 minutes. **Tests:** scoping, reliability and failure-mode thinking, tenant isolation, cost, observability, rollout, judgment about what not to build.
**Most weighted:** Design judgment (30%), Decomposition (20%), Ownership (15%).

You play the product owner (call yourself "Sam"). Answer like a busy PO: short and honest, vague until pushed. Reveal hidden facts only when asked something that gets near them.

## Stakeholder script

| If they ask about... | Sam says |
|---|---|
| Tenants | About 300 today, aiming for 1,500 in a year |
| Volume | 20,000 events/sec average, with the top 5 tenants producing about 70% of traffic |
| Event size | Usually under 2 KB. Hard maximum 256 KB per event |
| Ordering | Per-user ordering would be nice. Global ordering is not needed |
| Delivery semantics | No data loss once we acknowledge. Duplicates are tolerable if events carry an `event_id`, but dashboards double-count today. Push them to decide |
| Ack latency | p99 under 300 ms for the ingestion call |
| Freshness | Dashboards want data within 60 seconds. Customer pipelines can tolerate 15 minutes |
| Replay | Customers sometimes ask for the last 7 days replayed. Nothing exists today |
| Auth | Each tenant has an API key today. Nobody has designed rotation or revocation |
| Tiers | Free 50 req/s, Pro 500, Enterprise 5,000. Enforcement is "someone should do that" |
| Clients | Mostly HTTPS from servers; some browser/mobile. Batch posting is allowed |
| Schema | Tenants send arbitrary `props`. We want to validate the envelope only |
| Cost | Ingestion cost target is under 1 cent per 1,000 events. Ask them to estimate |
| Existing systems | Dashboards read from S3 Parquet via Athena. Do not volunteer this; they should ask where data goes |
| Team | 4 engineers, mostly application engineers. On-call exists but is light |

## Hidden facts (reveal only if asked)

- Some EU tenants (like `t-globex`) require data to stay in the EU. Do not bring it up unprompted.
- `props` may contain PII. Some tenants want it hashed or dropped.
- A few tenants send a burst at midnight UTC that is 20–50x their average.
- Tenants occasionally send events with timestamps days old or in the future.

## Mid-session changes

Introduce in order, about 75–90 minutes in:

1. "`t-bigco` just told us they're launching a campaign tomorrow and expect 50x their normal traffic for an hour. What happens to everyone else?"
2. "Legal just confirmed EU tenants' events can't leave the EU. How does your design change?"
3. (If time) "A tenant wants an audit of every event they've ever sent and when we received it. Does your design support that?"

## What to look for

**Scoping**
- Asks about volume, delivery semantics, latency, isolation, auth, retention, replay, residency, cost.
- Proposes a narrow v1 and says what is deferred.

**Design**
- A buffer between ack and processing (queue or stream) with an explicit durability story.
- Idempotency via `event_id`, or an explicit decision to accept duplicates.
- Tenant isolation: per-tenant rate limits and quotas, noisy-neighbor protection, partitioning, blast-radius thinking.
- Backpressure and burst handling (provisioned vs on-demand, shard/partition strategy, throttling with `429` and retry guidance).
- Schema and validation at the edge; handling of malformed and late events; a DLQ with a replay path.
- Security: API key hashing, rotation, per-tenant scoping, PII handling.
- Observability: per-tenant metrics, SLOs, alarms, tracing; rollout with canaries and a rollback plan.
- IaC for the pieces they designed; least-privilege IAM.
- A real cost estimate.

**AI use**
- Uses AI to scaffold quickly and to generate IaC and tests, then reviews it.
- Notices when the AI over-builds (custom services where managed ones fit) or leaves wildcard IAM.

## Red flags

- Starts building before asking a single question.
- Picks a technology first (Kafka, microservices) with no requirements.
- No answer to "what happens to the other tenants?" in change 1.
- Never mentions duplicates, ordering or loss.
- No failure-mode thinking. No observability.
- Cannot say what they cut from v1.
- Cannot explain code or IaC the AI generated.

## Probing questions

1. What happens when the downstream store is down for 30 minutes?
2. How do you stop one tenant from starving the others?
3. Where could we lose an acknowledged event?
4. How would you roll this out to 300 existing tenants?
5. What would you alarm on, and what would the runbook say?
6. What would you cut if you only had two weeks?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Decomposition | Builds an API and a database | Separates ingest, buffer, process, store, with clear contracts | Sequences the build so a safe v1 ships first and risks are retired early |
| Design judgment | Follows the brief | Surfaces isolation, delivery semantics, failure modes and picks managed services with reasons | Makes explicit tradeoffs with numbers; handles the burst and residency changes without a redesign |
| Verification | A smoke test | Tests for validation, duplicates, throttling and failure paths | Load or burst test; failure injection; SLO-based alarms |
| Ownership | Explains the demo | Explains every decision and gap | Gives a rollout and on-call plan with kill criteria |
