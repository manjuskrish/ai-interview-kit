# Interviewer guide: Cloud SWE, Mid/Senior (Order service)

**Time:** 90 minutes. **Tests:** idempotency under at-least-once delivery, partial batch failure, DLQ handling, least-privilege IAM, tests for failure modes.
**Most weighted:** Verification (25%), Prompt and context (20%), Design judgment (15%).

## Setup (3 minutes)

Candidate runs `pytest`. Everything fails with `NotImplementedError` (stub exercise). `python scripts/check_iam.py infra/template.yaml` reports 5 findings (three wildcard actions, two wildcard resources).

## Seeded issues and intentional ambiguity

| Issue | Where | Notes |
|---|---|---|
| **Latent trap:** `put_order()` is an existing unconditional write | `repository.py` | An AI that calls it in the consumer overwrites shipped orders on redelivery. The visible redelivery test catches this (status reset). A "get, then put" version also passes it but is a race |
| Wildcard IAM | `infra/template.yaml` | `sqs:*` and `dynamodb:*` on `*` for both functions. AI tends to leave or reproduce these |
| Transient vs permanent errors | `CANDIDATE.md` Part 2 | The spec names validation errors (permanent) and throttling (transient) but not "everything else". A strong candidate decides and says why. The reference treats unknown errors as retryable |
| DLQ send itself fails | `CANDIDATE.md` Part 2 | Not specified. Strong candidates ask. Reference reports the message as a batch failure |
| Idempotency key semantics | `CANDIDATE.md` Part 1 | Same key with a different body gives the same `order_id`. A strong candidate raises this |
| Visibility timeout and retries | `infra/template.yaml` | `maxReceiveCount: 5` and the 60 s timeout interact with the Lambda timeout |

## AI traps to watch for

- Using `put_order` or a get-then-put in `handle_batch`.
- Raising from `handle_batch` instead of returning `batchItemFailures`, which retries the **whole** batch.
- Catching `Exception` around the whole loop so one bad record loses the rest.
- Swallowing errors with a log line and returning success.
- `Action: "*"` retained, or replaced by another broad grant like `dynamodb:*` on the table.
- Tests that only cover the happy path, or that mock the repository so the conditional write is never exercised.
- Creating boto3 clients at import time (breaks under moto).

## Mid-session change (at about 55 minutes)

Say: "Finance wants a `total_cents` field on every order, computed from a price lookup, and orders with a total over $10,000 should be held for review rather than saved as RECEIVED. How would you add that?" Watch where they put the logic, what happens to messages already in the queue, and whether they update tests first.

## Probing questions

1. What happens if the consumer Lambda times out after saving the order but before returning?
2. Why return `batchItemFailures` instead of raising?
3. How do you know your idempotency holds when two consumers process the same order at once?
4. How would you replay messages from the DLQ safely?
5. What would you alarm on?
6. Which IAM actions does each function really need, and how did you check?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Prompt and context | Pastes stubs and test errors | Gives the AI the spec, existing models and test helpers, and calls out the legacy `put_order` trap | Constrains the AI on invariants (conditional write, partial failure) before it generates code |
| Verification | Runs given tests | Adds tests for poison messages, duplicates in one batch, unexpected exceptions, header case | Runs `check_iam.py`, verifies IAM against actual API calls, tests concurrency or ordering |
| Design judgment | Follows the spec | Decides what counts as transient and explains it | Weighs DLQ and retry settings with the Lambda timeout and visibility timeout |
| Ownership | Explains the happy path | Explains each failure mode | Describes monitoring, replay and rollout |

## Reference materials

- `_interviewer/solution/` is a complete implementation including a least-privilege template.
- `_interviewer/hidden_tests/` has `test_hidden.py` (behaviour) and `test_iam.py` (template check). Run both after the session.
