"""Order model and validation."""
from __future__ import annotations

import json
from dataclasses import dataclass


class ValidationError(ValueError):
    """The payload is not a valid order. Retrying will not help."""


@dataclass
class OrderItem:
    sku: str
    qty: int


@dataclass
class Order:
    order_id: str
    customer_id: str
    items: list[OrderItem]

    @classmethod
    def from_message(cls, body: str) -> "Order":
        """Parse an SQS message body. Raises ValidationError if it is not a valid order message."""
        try:
            payload = json.loads(body)
        except (TypeError, ValueError) as exc:
            raise ValidationError("message is not valid JSON") from exc
        customer_id, items = validate_order_payload(payload)
        order_id = payload.get("order_id")
        if not isinstance(order_id, str) or not order_id:
            raise ValidationError("order_id is required")
        return cls(order_id, customer_id, [OrderItem(**item) for item in items])


def validate_order_payload(payload) -> tuple[str, list[dict]]:
    """Validate {"customer_id", "items": [{"sku", "qty"}]}. Returns (customer_id, clean_items)."""
    if not isinstance(payload, dict):
        raise ValidationError("payload must be a JSON object")
    customer_id = payload.get("customer_id")
    if not isinstance(customer_id, str) or not customer_id:
        raise ValidationError("customer_id is required")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise ValidationError("items must be a non-empty list")
    clean = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("sku"), str) or not item["sku"]:
            raise ValidationError("each item needs a sku")
        qty = item.get("qty")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValidationError("qty must be a positive integer")
        clean.append({"sku": item["sku"], "qty": qty})
    return customer_id, clean
