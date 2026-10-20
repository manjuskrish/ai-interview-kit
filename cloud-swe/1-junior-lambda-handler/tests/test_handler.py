import boto3
from conftest import BUCKET, OTHER_BUCKET, create_table
from helpers import make_event, put, rows_for

from handler import lambda_handler


def test_counts_objects_and_bytes_for_the_customer(aws):
    for i in range(3):
        put(aws.s3, BUCKET, f"reports/acme/r{i}.csv", b"12345")
    put(aws.s3, BUCKET, "reports/other/r.csv", b"zzzzzzzzzz")

    result = lambda_handler(make_event(BUCKET, "reports/acme/r0.csv"), None)

    assert result["processed"][0]["customer"] == "acme"
    assert result["processed"][0]["object_count"] == 3
    (row,) = rows_for(aws.table, "acme")
    assert row["object_count"] == 3
    assert row["total_bytes"] == 15


def test_counts_more_than_1000_objects(aws):
    for i in range(1050):
        put(aws.s3, BUCKET, f"reports/acme/r{i:04d}.csv")

    result = lambda_handler(make_event(BUCKET, "reports/acme/r0000.csv"), None)

    assert result["processed"][0]["object_count"] == 1050


def test_repeat_invocation_leaves_one_row(aws):
    put(aws.s3, BUCKET, "reports/acme/r.csv")
    event = make_event(BUCKET, "reports/acme/r.csv")

    lambda_handler(event, None)
    lambda_handler(event, None)

    assert len(rows_for(aws.table, "acme")) == 1


def test_reads_bucket_from_the_event(aws):
    put(aws.s3, OTHER_BUCKET, "reports/globex/a.csv")
    put(aws.s3, OTHER_BUCKET, "reports/globex/b.csv")

    result = lambda_handler(make_event(OTHER_BUCKET, "reports/globex/a.csv"), None)

    assert result["processed"][0]["object_count"] == 2


def test_reads_table_name_from_the_environment(aws, monkeypatch):
    other_table = create_table("report-index-v2")
    monkeypatch.setenv("TABLE_NAME", "report-index-v2")
    put(aws.s3, BUCKET, "reports/acme/r.csv")

    lambda_handler(make_event(BUCKET, "reports/acme/r.csv"), None)

    assert len(rows_for(other_table, "acme")) == 1
    assert rows_for(aws.table, "acme") == []
