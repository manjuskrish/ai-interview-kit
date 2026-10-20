from types import SimpleNamespace

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def aws(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    with mock_aws():
        sqs = boto3.client("sqs")
        dlq_url = sqs.create_queue(QueueName="orders-dlq")["QueueUrl"]
        queue_url = sqs.create_queue(QueueName="orders")["QueueUrl"]
        ddb = boto3.resource("dynamodb")
        table = ddb.create_table(
            TableName="orders-table",
            KeySchema=[{"AttributeName": "order_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "order_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        monkeypatch.setenv("ORDERS_TABLE", "orders-table")
        monkeypatch.setenv("ORDERS_QUEUE_URL", queue_url)
        monkeypatch.setenv("DLQ_URL", dlq_url)
        yield SimpleNamespace(sqs=sqs, queue_url=queue_url, dlq_url=dlq_url, table=table)
