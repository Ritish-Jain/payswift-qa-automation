"""Test 2: negative and validation flows. Every case asserts the exact UI error text.

The locked-out user case mirrors PaySwift's "account locked after 3 failed PIN
attempts" rule: the server rejects a known user and the UI must say why.
"""
from __future__ import annotations

import pytest

from framework.data_loader import load

pytestmark = [pytest.mark.ui, pytest.mark.negative]

LOGIN_CASES = load("users")["invalid_login_cases"]
CHECKOUT_CASES = load("checkout")["validation_cases"]


@pytest.mark.parametrize("case", LOGIN_CASES, ids=[c["id"] for c in LOGIN_CASES])
def test_login_rejected_with_exact_message(login_page, case):
    login_page.attempt_login(case["username"], case["password"])

    assert login_page.error_message() == case["expected_error"]
    assert login_page.is_displayed(), "User should remain on the login screen"


@pytest.mark.parametrize("case", CHECKOUT_CASES, ids=[c["id"] for c in CHECKOUT_CASES])
def test_checkout_form_rejects_missing_fields(logged_in, case):
    first_item = load("checkout")["happy_path"]["items"][0]
    info_page = logged_in.add_to_cart(first_item).open_cart().checkout()

    info_page.fill(case["first_name"], case["last_name"], case["postal_code"])
    actual = info_page.submit_expecting_error()

    assert actual == case["expected_error"]
    assert info_page.is_displayed(), "User should not advance to the overview with invalid input"
