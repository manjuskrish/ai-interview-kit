"""Tools the agent can call (reference solution)."""

ORDERS = {
    "A100": "shipped",
    "A101": "processing",
    "A102": "delivered",
}


def echo(text):
    return text


def add(a, b):
    return a + b


def get_order_status(order_id):
    return ORDERS[order_id]


TOOLS = {
    "echo": echo,
    "add": add,
    "get_order_status": get_order_status,
}
