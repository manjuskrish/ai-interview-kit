import json


def order_msg(order_id="ord_1", customer_id="c1", items=None):
    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": items or [{"sku": "S1", "qty": 2}],
    }


def api_event(body, idempotency_key="key-1", header_name="Idempotency-Key"):
    headers = {header_name: idempotency_key} if idempotency_key else {}
    return {"headers": headers, "body": body if isinstance(body, str) else json.dumps(body)}


def sqs_event(*bodies):
    return {
        "Records": [
            {"messageId": f"m{i}", "body": b if isinstance(b, str) else json.dumps(b)}
            for i, b in enumerate(bodies)
        ]
    }


def receive_all(sqs, queue_url):
    return sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10).get("Messages", [])
