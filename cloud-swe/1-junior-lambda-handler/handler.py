"""Summarizes a customer's report objects whenever a new report lands in S3."""
import time
import uuid

import boto3

BUCKET = "acme-prod-reports"
TABLE = "report-index"


def lambda_handler(event, context):
    record = event["Records"][0]
    key = record["s3"]["object"]["key"]
    customer = key.split("/")[1]

    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=f"reports/{customer}/")
    objects = response.get("Contents", [])

    table = boto3.resource("dynamodb").Table(TABLE)
    table.put_item(
        Item={
            "pk": f"{customer}#{uuid.uuid4()}",
            "customer": customer,
            "object_count": len(objects),
            "total_bytes": sum(o["Size"] for o in objects),
            "updated_at": int(time.time()),
        }
    )

    return {"processed": [{"customer": customer, "object_count": len(objects)}]}
