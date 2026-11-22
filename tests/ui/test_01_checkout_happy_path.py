"""Test 1 - happy path: login, add items, checkout and check the totals.

Same flow as a PaySwift transfer: select, review amount, confirm, receipt.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from framework.data_loader import load_test_data
from framework.money import has_two_decimals, round_half_up

pytestmark = [pytest.mark.ui, pytest.mark.smoke]


def test_checkout_happy_path(products_page):
    data = load_test_data("checkout")["happy_path"]
    catalog = load_test_data("products")["catalog"]

    for name in data["items"]:
        products_page.add_product_to_cart(name)

    cart = products_page.open_cart()
    for name in data["items"]:
        assert cart.has_item(name), f"'{name}' missing from cart"

    customer = data["customer"]
    overview = (
        cart.proceed_to_checkout()
        .fill_details(customer["first_name"], customer["last_name"], customer["postal_code"])
        .click_continue()
    )
    summary = overview.get_order_summary()

    expected_item_total = sum((catalog[name]["price"] for name in data["items"]), Decimal("0"))
    expected_tax = round_half_up(expected_item_total * data["tax_rate"])
    expected_total = expected_item_total + expected_tax

    for field, value in (("item_total", summary.item_total), ("tax", summary.tax), ("total", summary.total)):
        assert has_two_decimals(value), f"{field} shown with more than 2 decimals: {summary.raw_text[field]!r}"
    assert summary.item_total == expected_item_total, summary.raw_text
    assert summary.tax == expected_tax, summary.raw_text
    assert summary.total == expected_total, summary.raw_text
    assert summary.total == summary.item_total + summary.tax, "Total does not reconcile with item total + tax"

    complete = overview.click_finish()
    assert complete.is_order_confirmed(data["confirmation_header"])
