# Exercise: Fix the Lambda handler (45 minutes)

Use your AI assistant however you like. We want to see how you work with it. Talk through what you are doing as you go.

## Context

When a report file lands in S3 under `reports/<customer>/...`, an S3 event invokes `lambda_handler` in `handler.py`. The handler counts that customer's report objects and total bytes, and stores a summary row in DynamoDB.

- The DynamoDB table has a string partition key `pk`. Use the customer name as `pk`.
- The table name comes from the `TABLE_NAME` environment variable.
- `events/sample_s3_event.json` shows the event shape.
- Tests use `moto` to simulate AWS, so you need no AWS account. Run `pytest` to start.

## Part 1: fix the handler (about 30 minutes)

The handler has bugs. Run the tests, reproduce each failure and fix it. Requirements:

1. Count **all** of a customer's objects, however many there are.
2. Re-running the handler for the same customer (S3 events are delivered at least once) must leave exactly one row for that customer.
3. Read the bucket from the event and the table name from `TABLE_NAME`. Do not hardcode either.
4. An event can contain several records. Handle each one.
5. S3 URL-encodes keys in events (a space arrives as `+`). Decode them.
6. Ignore keys that are not under `reports/<customer>/`. They must not raise.

The handler returns `{"processed": [{"customer": ..., "object_count": ...}, ...]}`.

## Part 2: extend it (about 10 minutes)

Add a `latest_modified` field (ISO 8601 string, the newest `LastModified` among the customer's objects) to the summary row. Add a test for it.

## Part 3: walk us through it (about 5 minutes)

Be ready to explain what was wrong, how you know it is fixed, and what could still go wrong in production.
