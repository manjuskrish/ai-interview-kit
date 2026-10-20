# Exercise: Multi-tenant event ingestion service (2 hours)

Use your AI assistant however you like. There is no starter code. You are building this the way you would at work, and the interviewer plays the product owner.

## The brief

> We are a B2B analytics product. Customers (tenants) send us product events from their apps, and we make those events available to our dashboards and to customers' own pipelines. Today each tenant integration is custom. We want one ingestion service that every tenant uses. Design it and build the core.

That is the whole brief. Ask the product owner whatever you need. Decide what to build, what to leave out, and how you will know it is reliable.

## What we have for you

- `data/tenants.json`: a few example tenants with their plan tier.
- `data/sample_events.jsonl`: example events from several tenants.
- `docker-compose.yml`: LocalStack, in case you want to run AWS services locally. You do not have to use it. You may use any language, framework, cloud services (real or simulated) and infrastructure-as-code tool you like.
- No cloud accounts are provided. Design for AWS, but build and test locally.

## What to hand over

1. **A working core.** At least the ingestion path end to end (accept events, validate, store or forward them durably), with tests.
2. **Infrastructure as code** for the parts you designed, even if not deployed.
3. **A short `DESIGN.md`.** Architecture, key decisions and tradeoffs, failure modes, how you isolate tenants, how you would observe and roll it out, what you did not build and why.

## Time plan (suggested)

| Time | Focus |
|---|---|
| 0–15 min | Questions and scoping with the product owner |
| 15–90 min | Design and build the core |
| 90–105 min | Update for new information from the product owner |
| 105–120 min | Walkthrough and discussion |
