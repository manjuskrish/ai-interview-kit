"""DynamoDB access for orders (reference solution)."""
from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from . import config
from .models import Order


def _to_item(order: Order) -> dict:
    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "items": [{"sku": i.sku, "qty": i.qty} for i in order.items],
        "status": "RECEIVED",
    }


class OrderRepository:
    def __init__(self, table=None):
        self._table = table or boto3.resource("dynamodb").Table(config.orders_table())

    def get_order(self, order_id: str) -> dict | None:
        return self._table.get_item(Key={"order_id": order_id}).get("Item")

    def put_order(self, order: Order) -> None:
        """Legacy unconditional write, used by the nightly import job. Overwrites any existing order."""
        self._table.put_item(Item=_to_item(order))

    def put_order_once(self, order: Order) -> bool:
        """Save the order only if its order_id does not exist yet. True if created, False if a duplicate."""
        try:
            self._table.put_item(
                Item=_to_item(order),
                ConditionExpression="attribute_not_exists(order_id)",
            )
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise
