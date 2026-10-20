"""Tool registry and the demo tools the support agent can call."""
from __future__ import annotations

from typing import Any, Callable

ORDERS = {
    "A100": {"customer": "c1", "total": 42.00, "status": "shipped"},
    "A101": {"customer": "c1", "total": 180.00, "status": "delivered"},
    "A102": {"customer": "c2", "total": 95.50, "status": "processing"},
}


class ToolError(Exception):
    """A tool failed in a way the model should be told about."""


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._tools[name] = fn

    def names(self) -> list[str]:
        return sorted(self._tools)

    def call(self, name: str, args: dict[str, Any]) -> Any:
        if name not in self._tools:
            raise ToolError(f"unknown tool: {name}")
        try:
            return self._tools[name](**args)
        except ToolError:
            raise
        except TypeError as exc:
            raise ToolError(f"bad arguments for {name}: {exc}") from exc


def lookup_order(order_id: str) -> dict:
    order = ORDERS.get(order_id)
    if order is None:
        raise ToolError(f"no such order: {order_id}")
    return {"order_id": order_id, **order}


def issue_refund(order_id: str, amount: float) -> dict:
    order = ORDERS.get(order_id)
    if order is None:
        raise ToolError(f"no such order: {order_id}")
    if amount <= 0 or amount > order["total"]:
        raise ToolError("refund amount must be between 0 and the order total")
    return {"order_id": order_id, "refunded": amount}


def escalate_to_human(reason: str) -> dict:
    return {"ticket": "T-1", "reason": reason}


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("lookup_order", lookup_order)
    registry.register("issue_refund", issue_refund)
    registry.register("escalate_to_human", escalate_to_human)
    return registry
