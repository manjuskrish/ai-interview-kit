from types import SimpleNamespace

import boto3
import pytest
from moto import mock_aws

BUCKET = "acme-prod-reports"
OTHER_BUCKET = "tenant-b-reports"
TABLE = "report-index"


def create_table(name):
    ddb = boto3.resource("dynamodb")
    ddb.create_table(
        TableName=name,
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    return ddb.Table(name)


@pytest.fixture
def aws(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("TABLE_NAME", TABLE)
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET)
        s3.create_bucket(Bucket=OTHER_BUCKET)
        table = create_table(TABLE)
        yield SimpleNamespace(s3=s3, table=table)
