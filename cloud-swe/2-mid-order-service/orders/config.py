"""Resource names come from environment variables set by the SAM template."""
import os


def orders_table() -> str:
    return os.environ["ORDERS_TABLE"]


def queue_url() -> str:
    return os.environ["ORDERS_QUEUE_URL"]


def dlq_url() -> str:
    return os.environ["DLQ_URL"]
