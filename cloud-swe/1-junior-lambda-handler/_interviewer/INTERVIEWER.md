# Interviewer guide: Cloud SWE, Junior (Lambda handler)

**Time:** 45 minutes. **Tests:** reproducing and fixing common cloud-handler defects; verifying AI fixes against a simulated AWS.
**Most weighted:** Verification (30%), Recovery (25%).

## Setup (2 minutes)

Candidate runs `pytest`. `test_counts_objects_and_bytes_for_the_customer` passes; the other four fail. The 1,050-object test takes a few seconds.

## Seeded issues

| Issue | Where | Visible test |
|---|---|---|
| No pagination: `list_objects_v2` returns at most 1,000 keys | `s3.list_objects_v2` | yes |
| Non-idempotent write: `pk` includes a random UUID, so retries add rows | `uuid.uuid4()` in the key | yes |
| Hardcoded bucket | `BUCKET` constant | yes |
| Hardcoded table name | `TABLE` constant | yes |
| Only `Records[0]` is processed | `event["Records"][0]` | hidden |
| Event keys are URL-encoded (`+` for space) and are not decoded | `record["s3"]["object"]["key"]` | hidden |
| Keys outside `reports/<customer>/` raise `IndexError` | `key.split("/")[1]` | hidden |

## AI traps to watch for

- **Manual pagination loop with a bug.** Hand-written `ContinuationToken` loops that skip the last page or loop forever. A paginator is the idiomatic fix.
- **Idempotency by "check then put".** Reading first and writing second is a race. The overwrite-by-key fix is simpler and correct.
- **Adding retries, sleeps or timeouts** as a "fix".
- **Module-level boto3 clients.** Work in Lambda, but break under moto if created before the mock starts. Watch whether the candidate understands why a test fails after this change.
- **Accepting the AI fix without reproducing the failure first.**
- **Unit test that asserts the mock was called** instead of asserting the result.

## Mid-session change (at about 30 minutes)

Part 2 is the change. Watch whether the candidate writes the test first, handles an empty bucket (no `Contents`, so `latest_modified` is missing) and formats the timestamp consistently.

## Probing questions

1. Why does S3 deliver events more than once, and what does that mean for this handler?
2. What happens if one customer has 5 million objects? Is listing the right approach?
3. What would you do if the Lambda times out halfway through a batch of records?
4. Which IAM permissions does this function need?
5. What would you alarm on?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Verification | Runs the tests after each fix | Reproduces each failure first; adds a test for a case not provided (multiple records, keys with `+`) | Also reasons about the empty-bucket and unrelated-key cases |
| Recovery | Re-prompts when a fix fails | Reads the failure and tells the AI the specific cause | Spots a race or loop bug in the AI's code by reading it |
| Ownership | Explains the happy path | Explains why each fix is needed | Raises the scale limits of listing and what to monitor |

## Reference materials

- `_interviewer/solution/handler.py` passes all visible tests. It does not implement Part 2's `latest_modified`; the hidden tests do not require it.
- `_interviewer/hidden_tests/test_hidden.py` covers the hidden issues. Run it after the session.
