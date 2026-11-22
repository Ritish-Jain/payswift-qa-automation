"""Contract checks for transfer initiation against the public mock endpoint.

jsonplaceholder echoes the posted body and adds an integer "id", which stands in for
the server-generated transaction id. The response body is parsed with Decimal so the
amount is compared exactly, never as a float.
"""
from __future__ import annotations

import json
from decimal import Decimal

import pytest
from jsonschema import Draft202012Validator

from framework.money import has_at_most_two_decimals

pytestmark = pytest.mark.api


def _to_json_body(payload: dict) -> str:
    """Serialise Decimal amounts as JSON numbers, refusing any value a float would distort."""

    def encode(value):
        if isinstance(value, Decimal):
            as_float = float(value)
            if Decimal(repr(as_float)) != value.normalize():
                raise ValueError(f"{value} cannot be sent as a JSON number without precision loss")
            return as_float
        raise TypeError(f"Cannot serialise {type(value)}")

    return json.dumps(payload, default=encode)


@pytest.fixture(scope="module")
def transfer_response(api_session, api_base_url, transfer_data):
    url = f"{api_base_url}{transfer_data['endpoint']}"
    # Warm-up: open the keep-alive connection first so the timed POST below measures API
    # latency, not one-off DNS + TCP + TLS setup (often 300 ms+ on its own).
    api_session.get(f"{api_base_url}/posts/1", timeout=10)
    response = api_session.post(url, data=_to_json_body(transfer_data["transfer_request"]), timeout=10)
    return response


@pytest.fixture(scope="module")
def response_body(transfer_response):
    return json.loads(transfer_response.text, parse_float=Decimal)


def test_returns_201_created(transfer_response):
    assert transfer_response.status_code == 201, transfer_response.text


def test_latency_under_threshold(transfer_response, transfer_data):
    elapsed_ms = transfer_response.elapsed.total_seconds() * 1000
    assert elapsed_ms < transfer_data["max_latency_ms"], f"Took {elapsed_ms:.0f} ms"


def test_content_type_is_json(transfer_response):
    content_type = transfer_response.headers.get("Content-Type", "")
    assert content_type.split(";")[0].strip().lower() == "application/json", content_type


def test_body_matches_schema(transfer_response, transfer_schema):
    body = transfer_response.json()  # jsonschema needs native numbers
    errors = sorted(Draft202012Validator(transfer_schema).iter_errors(body), key=lambda e: e.path)
    assert not errors, "\n".join(f"{list(e.path)}: {e.message}" for e in errors)


@pytest.mark.parametrize("field", ["senderId", "receiverId", "currency", "idempotencyKey"])
def test_string_fields_are_echoed(response_body, transfer_data, field):
    assert response_body[field] == transfer_data["transfer_request"][field]


def test_amount_echoed_exactly_with_two_decimal_precision(response_body, transfer_data):
    sent = transfer_data["transfer_request"]["amount"]
    received = response_body["amount"]
    assert isinstance(received, Decimal), f"amount should be a JSON number, got {type(received).__name__}"
    assert received == sent
    assert has_at_most_two_decimals(received)


def test_transaction_id_is_generated(response_body):
    txn_id = response_body.get("id")
    assert isinstance(txn_id, int) and not isinstance(txn_id, bool), f"id={txn_id!r}"
    assert txn_id > 0
