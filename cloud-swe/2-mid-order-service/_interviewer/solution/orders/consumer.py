"""SQS consumer (reference solution)."""
from __future__ import annotations

import logging

import boto3

from . import config
from .models import Order, ValidationError
from .repository import OrderRepository

logger = logging.getLogger(__name__)


def handle_batch(event: dict, repo=None, sqs=None) -> dict:
    repo = repo or OrderRepository()
    failures = []

    for record in event.get("Records", []):
        message_id = record["messageId"]
        body = record.get("body", "")

        try:
            order = Order.from_message(body)
        except ValidationError as exc:
            # Permanent failure: retrying cannot help, so park it in the DLQ right away.
            try:
                sqs = sqs or boto3.client("sqs")
                sqs.send_message(
                    QueueUrl=config.dlq_url(),
                    MessageBody=body if isinstance(body, str) else str(body),
                    MessageAttributes={"error": {"DataType": "String", "StringValue": str(exc)[:200]}},
                )
            except Exception:
                logger.exception("could not send message %s to the DLQ", message_id)
                failures.append({"itemIdentifier": message_id})
            continue

        try:
            repo.put_order_once(order)  # False (duplicate delivery) is a success
        except Exception:
            # Transient or unexpected: let SQS retry just this message.
            logger.exception("failed to save order %s", order.order_id)
            failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": failures}
