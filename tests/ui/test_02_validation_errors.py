"""Test 2 - negative cases: invalid login and checkout validation, checks exact error text.

locked_out_user is similar to PaySwift locking the account after 3 wrong PINs.
"""
from __future__ import annotations

import pytest

from framework.data_loader import load_test_data

pytestmark = [pytest.mark.ui, pytest.mark.negative]

LOGIN_CASES = load_test_data("users")["invalid_login_cases"]
CHECKOUT_CASES = load_test_data("checkout")["validation_cases"]


@pytest.mark.parametrize("case", LOGIN_CASES, ids=[c["id"] for c in LOGIN_CASES])
def test_invalid_login(login_page, case):
    login_page.try_login(case["username"], case["password"])

    assert login_page.get_error_message() == case["expected_error"]
    assert login_page.is_displayed(), "User should remain on the login screen"


@pytest.mark.parametrize("case", CHECKOUT_CASES, ids=[c["id"] for c in CHECKOUT_CASES])
def test_checkout_missing_fields(products_page, case):
    first_item = load_test_data("checkout")["happy_path"]["items"][0]
    info_page = products_page.add_product_to_cart(first_item).open_cart().proceed_to_checkout()

    info_page.fill_details(case["first_name"], case["last_name"], case["postal_code"])
    actual = info_page.continue_and_get_error()

    assert actual == case["expected_error"]
    assert info_page.is_displayed(), "User should not advance to the overview with invalid input"
