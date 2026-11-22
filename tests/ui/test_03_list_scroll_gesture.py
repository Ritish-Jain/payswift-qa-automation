"""Test 3: swipe through a scrollable list to find an item that starts off-screen,
then open it and verify its details.

In PaySwift terms this is "scroll transaction history to a specific transaction and
check its amount and narration".
"""
from __future__ import annotations

import pytest

from framework.data_loader import load
from framework.money import parse_amount

pytestmark = [pytest.mark.ui, pytest.mark.gesture]


def test_swipe_to_last_product_and_verify_details(logged_in):
    products_data = load("products")
    target = products_data["scroll_target"]
    expected = products_data["catalog"][target]

    detail = logged_in.scroll_to_product(target).open_product(target)
    name, description = detail.name_and_description()

    assert name == target
    assert description.startswith(expected["description_starts_with"])
    assert parse_amount(detail.price_text()) == expected["price"]
