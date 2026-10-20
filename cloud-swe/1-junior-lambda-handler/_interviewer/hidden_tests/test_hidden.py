from conftest import BUCKET
from helpers import make_event, put, rows_for

from handler import lambda_handler


def test_every_record_in_the_event_is_processed(aws):
    put(aws.s3, BUCKET, "reports/acme/a.csv")
    put(aws.s3, BUCKET, "reports/globex/a.csv")
    put(aws.s3, BUCKET, "reports/globex/b.csv")

    result = lambda_handler(make_event(BUCKET, "reports/acme/a.csv", "reports/globex/b.csv"), None)

    counts = {p["customer"]: p["object_count"] for p in result["processed"]}
    assert counts == {"acme": 1, "globex": 2}
    assert len(rows_for(aws.table, "acme")) == 1
    assert len(rows_for(aws.table, "globex")) == 1


def test_url_encoded_keys_are_decoded(aws):
    put(aws.s3, BUCKET, "reports/acme corp/Q1 report.csv")

    # S3 sends "acme corp" as "acme+corp" and "Q1 report" as "Q1+report".
    result = lambda_handler(make_event(BUCKET, "reports/acme+corp/Q1+report.csv"), None)

    assert result["processed"] == [{"customer": "acme corp", "object_count": 1}]
    assert len(rows_for(aws.table, "acme corp")) == 1


def test_keys_outside_reports_prefix_are_ignored(aws):
    result = lambda_handler(make_event(BUCKET, "README.txt", "reports/loose-file.csv", "other/acme/a.csv"), None)

    assert result == {"processed": []}
    assert aws.table.scan()["Items"] == []


def test_two_records_for_the_same_customer_write_one_row(aws):
    put(aws.s3, BUCKET, "reports/acme/a.csv")
    put(aws.s3, BUCKET, "reports/acme/b.csv")

    result = lambda_handler(make_event(BUCKET, "reports/acme/a.csv", "reports/acme/b.csv"), None)

    assert result["processed"] == [{"customer": "acme", "object_count": 2}]
    assert len(rows_for(aws.table, "acme")) == 1
