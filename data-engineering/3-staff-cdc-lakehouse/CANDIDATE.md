# Exercise: CDC into a lakehouse (2 hours)

Use your AI assistant however you like. There is no starter code. You are building this the way you would at work, and the interviewer plays the data platform owner.

## The brief

> Our orders service runs on a relational database. We publish its change events (inserts, updates, deletes) to a message bus. Analytics, finance and ML all want that data in our lakehouse, and today each team reads the database directly. We want one reliable pipeline that lands the changes in the lakehouse. Design it and build the core.

That is the whole brief. Ask the platform owner whatever you need. Decide what to build, what to leave out, and how you will know the data is right.

## What we have for you

- `data/cdc_sample.jsonl`: 19 example change events for an `orders` table.
- `tools/generate_cdc.py`: generates a larger, messier feed (duplicates, out-of-order delivery, deletes, a schema change). Run `python tools/generate_cdc.py --events 5000 > data/cdc_large.jsonl`.
- A Python environment. You may use any libraries (DuckDB, pandas, PySpark, Delta, Iceberg and so on) and any local storage that stands in for a lakehouse.
- No cloud accounts are provided. Design for a real lakehouse, but build and test locally.

Each event has: `lsn` (the source log position), `ts_ms` (when the change happened), `op` (`r` snapshot, `c` insert, `u` update, `d` delete), `source.table`, and `before` / `after` row images.

## What to hand over

1. **A working core.** Take the change events and produce the tables you decide the business needs, with tests that show it handles duplicates, out-of-order events and deletes.
2. **A way to check the data is right.** Show how you would know the lakehouse matches the source, and how you would notice when it stops matching.
3. **A short `DESIGN.md`.** Architecture, key decisions and tradeoffs, failure and recovery, schema changes, backfills, monitoring, what you did not build and why.

## Time plan (suggested)

| Time | Focus |
|---|---|
| 0–15 min | Questions and scoping with the platform owner |
| 15–90 min | Design and build the core |
| 90–105 min | Update for new information from the platform owner |
| 105–120 min | Walkthrough and discussion |
