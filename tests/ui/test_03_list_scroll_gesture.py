"""Test 3: swipe through a scrollable list to find an item that starts off-screen,
then open it and verify its details.

In PaySwift terms this is "scroll transaction history to a specific transaction and
check its amount and narration".
"""
from __future__ import annotations

import pytest

from framework.data_loader import load_test_data
from framework.money import parse_amount

pytestmark = [pytest.mark.ui, pytest.mark.gesture]


def test_scroll_to_product(products_page):
    products_data = load_test_data("products")
    target = products_data["scroll_target"]
    expected = products_data["catalog"][target]

    detail = products_page.scroll_to_product(target).open_product(target)
    name, description = detail.get_name_and_description()

    assert name == target
    assert description.startswith(expected["description_starts_with"])
    assert parse_amount(detail.get_price()) == expected["price"]
