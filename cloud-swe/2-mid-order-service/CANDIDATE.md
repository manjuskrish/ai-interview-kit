# Exercise: Complete the order service (90 minutes)

Use your AI assistant however you like. We want to see how you work with it. Ask us questions whenever the spec is unclear.

## Context

An order-intake service on AWS: `POST /orders` (API Gateway + Lambda) validates an order and puts it on an SQS queue. A second Lambda consumes the queue and saves each order to DynamoDB.

```
client -> API Lambda (orders/api.py) -> SQS orders queue -> consumer Lambda (orders/consumer.py) -> DynamoDB
                                                  \-> dead-letter queue
```

| File | State |
|---|---|
| `orders/models.py` | Done. Validation and the `Order` model |
| `orders/config.py` | Done. Reads resource names from environment variables |
| `orders/repository.py` | **Incomplete.** `put_order_once()` is not implemented. `put_order()` is the legacy unconditional write used by an old import job |
| `orders/api.py` | **Incomplete.** `create_order()` |
| `orders/consumer.py` | **Incomplete.** `handle_batch()` |
| `infra/template.yaml` | SAM template. Needs a security review |

Tests use `moto` to simulate AWS, so you need no AWS account. Read the existing code first, then run `pytest`.

## Part 1: the API handler (about 20 minutes)

`create_order(event, context=None, sqs=None)` handles an API Gateway proxy event.

- Require an `Idempotency-Key` header (header names are case-insensitive). Missing: respond 400.
- The body is JSON: `{"customer_id": str, "items": [{"sku": str, "qty": int > 0}]}`. Invalid JSON or an invalid order: respond 400 with `{"error": "<reason>"}`.
- The `order_id` is derived from the idempotency key: `"ord_" + first 16 hex chars of sha256(key)`. The same key always gives the same `order_id`.
- Send `{"order_id", "customer_id", "items"}` as JSON to the queue (`ORDERS_QUEUE_URL`) and respond 202 with `{"order_id": ...}`.

## Part 2: repository and consumer (about 35 minutes)

SQS delivers messages **at least once**, and one bad message must not block the others in a batch.

- `OrderRepository.put_order_once(order)` saves the order only if that `order_id` does not exist yet. Return `True` if created, `False` if it already existed. Other errors propagate.
- `handle_batch(event, repo=None, sqs=None)` handles an SQS event and returns `{"batchItemFailures": [{"itemIdentifier": <messageId>}, ...]}`.
  - A valid message is saved once. A redelivered message is not an error, and must not overwrite the existing order.
  - A **malformed or invalid** message (permanent failure) is sent to the dead-letter queue (`DLQ_URL`) with its original body, and is not reported as a batch failure.
  - A **transient** failure (for example DynamoDB throttling) is reported as a batch item failure so SQS retries just that message.

## Part 3: tests (about 20 minutes)

Add tests for behaviour the existing tests do not cover. Focus on what is most likely to hurt in production.

## Part 4: least-privilege IAM (about 10 minutes)

`infra/template.yaml` grants more than the functions need. Tighten the permissions, then run:

```bash
python scripts/check_iam.py infra/template.yaml
```

## Part 5: walk us through it (about 5 minutes)

Be ready to explain your design, anything in the spec you had to interpret, and what you would add before shipping.
