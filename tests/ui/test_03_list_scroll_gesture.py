"""Test 3 - scroll the product list to an item that is off-screen and check its details.

Like scrolling transaction history in PaySwift to find a transaction.
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
