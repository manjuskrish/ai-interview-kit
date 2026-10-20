"""POST /orders (reference solution)."""
from __future__ import annotations

import hashlib
import json

import boto3

from . import config
from .models import ValidationError, validate_order_payload


def _response(status: int, body: dict) -> dict:
    return {"statusCode": status, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body)}


def create_order(event: dict, context=None, sqs=None) -> dict:
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    idempotency_key = headers.get("idempotency-key")
    if not idempotency_key:
        return _response(400, {"error": "Idempotency-Key header is required"})

    try:
        payload = json.loads(event.get("body") or "")
    except (TypeError, ValueError):
        return _response(400, {"error": "body must be valid JSON"})

    try:
        customer_id, items = validate_order_payload(payload)
    except ValidationError as exc:
        return _response(400, {"error": str(exc)})

    order_id = "ord_" + hashlib.sha256(idempotency_key.encode()).hexdigest()[:16]
    sqs = sqs or boto3.client("sqs")
    sqs.send_message(
        QueueUrl=config.queue_url(),
        MessageBody=json.dumps({"order_id": order_id, "customer_id": customer_id, "items": items}),
    )
    return _response(202, {"order_id": order_id})
