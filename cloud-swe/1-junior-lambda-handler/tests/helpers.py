def make_event(bucket, *keys):
    """Build an S3 event with one record per key (keys are given already URL-encoded)."""
    return {
        "Records": [
            {
                "eventSource": "aws:s3",
                "eventName": "ObjectCreated:Put",
                "s3": {"bucket": {"name": bucket}, "object": {"key": key}},
            }
            for key in keys
        ]
    }


def put(s3, bucket, key, body=b"x"):
    s3.put_object(Bucket=bucket, Key=key, Body=body)


def rows_for(table, customer):
    return [i for i in table.scan()["Items"] if i["customer"] == customer]
