from botocore.exceptions import ClientError
from helpers import order_msg, receive_all, sqs_event

from orders.consumer import handle_batch
from orders.repository import OrderRepository


class FlakyRepo:
    """Throttles one specific order and delegates everything else to the real repository."""

    def __init__(self, real, bad_order_id):
        self.real = real
        self.bad_order_id = bad_order_id

    def put_order_once(self, order):
        if order.order_id == self.bad_order_id:
            error = {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "slow down"}}
            raise ClientError(error, "PutItem")
        return self.real.put_order_once(order)


def test_saves_a_new_order(aws):
    result = handle_batch(sqs_event(order_msg("ord_1")))

    assert result == {"batchItemFailures": []}
    assert aws.table.get_item(Key={"order_id": "ord_1"})["Item"]["customer_id"] == "c1"


def test_redelivery_does_not_overwrite_an_existing_order(aws):
    event = sqs_event(order_msg("ord_1"))
    handle_batch(event)
    aws.table.update_item(
        Key={"order_id": "ord_1"},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "SHIPPED"},
    )

    result = handle_batch(event)

    assert result == {"batchItemFailures": []}
    assert aws.table.get_item(Key={"order_id": "ord_1"})["Item"]["status"] == "SHIPPED"


def test_poison_message_goes_to_the_dlq_and_is_not_a_batch_failure(aws):
    result = handle_batch(sqs_event("{not json"))

    assert result == {"batchItemFailures": []}
    (message,) = receive_all(aws.sqs, aws.dlq_url)
    assert message["Body"] == "{not json"


def test_transient_failure_is_reported_for_that_message_only(aws):
    repo = FlakyRepo(OrderRepository(), bad_order_id="ord_flaky")

    result = handle_batch(sqs_event(order_msg("ord_ok"), order_msg("ord_flaky")), repo=repo)

    assert result == {"batchItemFailures": [{"itemIdentifier": "m1"}]}
    assert aws.table.get_item(Key={"order_id": "ord_ok"}).get("Item") is not None
