"""Tools the agent can call."""

ORDERS = {
    "A100": "shipped",
    "A101": "processing",
    "A102": "delivered",
}


def echo(text):
    return text


def add(a, b):
    return a + b


TOOLS = {
    "echo": echo,
    "add": add,
}
