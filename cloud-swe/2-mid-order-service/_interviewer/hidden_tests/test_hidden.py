import json

from botocore.exceptions import ClientError
from helpers import api_event, order_msg, receive_all, sqs_event

from orders.api import create_order
from orders.consumer import handle_batch
from orders.repository import OrderRepository


class FlakyRepo:
    def __init__(self, real, bad_order_id):
        self.real = real
        self.bad_order_id = bad_order_id

    def put_order_once(self, order):
        if order.order_id == self.bad_order_id:
            error = {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "slow down"}}
            raise ClientError(error, "PutItem")
        return self.real.put_order_once(order)


class BrokenRepo:
    def put_order_once(self, order):
        raise RuntimeError("something unexpected")


def test_mixed_batch_only_reports_the_transient_failure(aws):
    event = sqs_event(
        order_msg("ord_a"),
        "{not json",
        order_msg("ord_flaky"),
        order_msg("ord_a"),  # duplicate of the first message
    )

    result = handle_batch(event, repo=FlakyRepo(OrderRepository(), "ord_flaky"))

    assert result == {"batchItemFailures": [{"itemIdentifier": "m2"}]}
    assert aws.table.get_item(Key={"order_id": "ord_a"}).get("Item") is not None
    assert aws.table.get_item(Key={"order_id": "ord_flaky"}).get("Item") is None
    assert len(receive_all(aws.sqs, aws.dlq_url)) == 1


def test_unexpected_errors_are_retried_not_lost(aws):
    result = handle_batch(sqs_event(order_msg("ord_1")), repo=BrokenRepo())

    assert result == {"batchItemFailures": [{"itemIdentifier": "m0"}]}
    assert receive_all(aws.sqs, aws.dlq_url) == []


def test_schema_invalid_message_goes_to_the_dlq(aws):
    bad = json.dumps({"order_id": "ord_9", "customer_id": "c1", "items": []})

    result = handle_batch(sqs_event(bad))

    assert result == {"batchItemFailures": []}
    (message,) = receive_all(aws.sqs, aws.dlq_url)
    assert message["Body"] == bad
    assert aws.table.get_item(Key={"order_id": "ord_9"}).get("Item") is None


def test_put_order_once_reports_whether_it_created_the_order(aws):
    from orders.models import Order, OrderItem

    repo = OrderRepository()
    order = Order("ord_1", "c1", [OrderItem("S1", 1)])

    assert repo.put_order_once(order) is True
    assert repo.put_order_once(order) is False


def test_header_name_is_case_insensitive(aws):
    body = {"customer_id": "c1", "items": [{"sku": "S1", "qty": 1}]}

    response = create_order(api_event(body, header_name="idempotency-key"))

    assert response["statusCode"] == 202


def test_invalid_json_body_is_a_400(aws):
    response = create_order(api_event("{nope"))

    assert response["statusCode"] == 400
    assert receive_all(aws.sqs, aws.queue_url) == []


def test_order_id_is_derived_from_the_key(aws):
    import hashlib

    body = {"customer_id": "c1", "items": [{"sku": "S1", "qty": 1}]}

    response = create_order(api_event(body, "abc"))

    expected = "ord_" + hashlib.sha256(b"abc").hexdigest()[:16]
    assert json.loads(response["body"])["order_id"] == expected
