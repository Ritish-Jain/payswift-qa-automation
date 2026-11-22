"""Test 1: login and complete an end-to-end checkout, verifying the order totals.

Stands in for the PaySwift transfer flow: select payee (products), review amount
(overview), confirm (finish), receipt (complete screen).
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from framework.data_loader import load
from framework.money import has_at_most_two_decimals, round_money

pytestmark = [pytest.mark.ui, pytest.mark.smoke]


def test_login_and_checkout_totals_are_correct(logged_in):
    data = load("checkout")["happy_path"]
    catalog = load("products")["catalog"]

    products = logged_in
    for name in data["items"]:
        products.add_to_cart(name)

    cart = products.open_cart()
    for name in data["items"]:
        assert cart.contains_item(name), f"'{name}' missing from cart"

    customer = data["customer"]
    overview = (
        cart.checkout()
        .fill(customer["first_name"], customer["last_name"], customer["postal_code"])
        .continue_to_overview()
    )
    summary = overview.summary()

    expected_item_total = sum((catalog[name]["price"] for name in data["items"]), Decimal("0"))
    expected_tax = round_money(expected_item_total * data["tax_rate"])
    expected_total = expected_item_total + expected_tax

    for field, value in (("item_total", summary.item_total), ("tax", summary.tax), ("total", summary.total)):
        assert has_at_most_two_decimals(value), f"{field} shown with more than 2 decimals: {summary.raw[field]!r}"
    assert summary.item_total == expected_item_total, summary.raw
    assert summary.tax == expected_tax, summary.raw
    assert summary.total == expected_total, summary.raw
    assert summary.total == summary.item_total + summary.tax, "Total does not reconcile with item total + tax"

    complete = overview.finish()
    assert complete.shows_confirmation(data["confirmation_header"])
