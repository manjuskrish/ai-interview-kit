import json

from helpers import api_event, receive_all

from orders.api import create_order

VALID = {"customer_id": "c1", "items": [{"sku": "S1", "qty": 2}]}


def test_accepts_a_valid_order_and_enqueues_it(aws):
    response = create_order(api_event(VALID))

    assert response["statusCode"] == 202
    order_id = json.loads(response["body"])["order_id"]
    assert order_id.startswith("ord_")
    (message,) = receive_all(aws.sqs, aws.queue_url)
    assert json.loads(message["Body"]) == {"order_id": order_id, **VALID}


def test_rejects_a_missing_idempotency_key(aws):
    response = create_order(api_event(VALID, idempotency_key=None))

    assert response["statusCode"] == 400
    assert receive_all(aws.sqs, aws.queue_url) == []


def test_rejects_an_invalid_order(aws):
    bad = {"customer_id": "c1", "items": [{"sku": "S1", "qty": 0}]}

    response = create_order(api_event(bad))

    assert response["statusCode"] == 400
    assert "error" in json.loads(response["body"])


def test_same_key_gives_the_same_order_id(aws):
    first = json.loads(create_order(api_event(VALID, "abc"))["body"])["order_id"]
    second = json.loads(create_order(api_event(VALID, "abc"))["body"])["order_id"]

    assert first == second
