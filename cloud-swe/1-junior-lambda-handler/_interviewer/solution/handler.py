"""Summarizes a customer's report objects whenever a new report lands in S3 (reference solution)."""
import os
import time
from urllib.parse import unquote_plus

import boto3


def _customer_from_key(key):
    """Return the customer for keys shaped reports/<customer>/<file>, otherwise None."""
    parts = key.split("/")
    if len(parts) < 3 or parts[0] != "reports" or not parts[1]:
        return None
    return parts[1]


def _summarize(s3, bucket, customer):
    count = 0
    total = 0
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=f"reports/{customer}/"):
        for obj in page.get("Contents", []):
            count += 1
            total += obj["Size"]
    return count, total


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

    processed = []
    seen = set()
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        customer = _customer_from_key(key)
        if customer is None or (bucket, customer) in seen:
            continue
        seen.add((bucket, customer))

        count, total = _summarize(s3, bucket, customer)
        table.put_item(
            Item={
                "pk": customer,  # same key on every delivery: re-runs overwrite, never duplicate
                "customer": customer,
                "object_count": count,
                "total_bytes": total,
                "updated_at": int(time.time()),
            }
        )
        processed.append({"customer": customer, "object_count": count})

    return {"processed": processed}
