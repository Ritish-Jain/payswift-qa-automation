"""Fast checks for framework helpers. No device or network needed."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from appium.webdriver.common.appiumby import AppiumBy

from framework.config import load_capabilities, load_settings
from framework.locator import Locator
from framework.money import has_at_most_two_decimals, parse_amount, round_money
from locators.products_locators import ProductsLocators

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Item total: $45.98", Decimal("45.98")),
        ("Tax: $3.68", Decimal("3.68")),
        ("₹1,00,000.00", Decimal("100000.00")),
        ("$59.980000000000004", Decimal("59.980000000000004")),
        ("Balance: -12.50", Decimal("-12.50")),
    ],
)
def test_parse_amount_keeps_exact_digits(text, expected):
    assert parse_amount(text) == expected


def test_parse_amount_rejects_text_without_digits():
    with pytest.raises(ValueError):
        parse_amount("Total: $")


@pytest.mark.parametrize(
    "value, expected",
    [(Decimal("3.6784"), Decimal("3.68")), (Decimal("0.005"), Decimal("0.01")), (Decimal("10"), Decimal("10.00"))],
)
def test_round_money_half_up(value, expected):
    assert round_money(value) == expected


def test_precision_guard_flags_float_artifacts():
    assert has_at_most_two_decimals(Decimal("45.98"))
    assert not has_at_most_two_decimals(Decimal("59.980000000000004"))


def test_locator_resolves_per_platform_and_formats():
    locator = ProductsLocators.ITEM_TITLE_BY_NAME.format(name="Sauce Labs Onesie")
    assert locator.for_platform("android") == (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("test-Item title").text("Sauce Labs Onesie")',
    )
    assert locator.for_platform("ios") == (
        AppiumBy.IOS_PREDICATE,
        'name == "test-Item title" AND label == "Sauce Labs Onesie"',
    )


def test_accessibility_id_locator_is_shared_across_platforms():
    locator = Locator.accessibility_id("test-LOGIN")
    assert locator.for_platform("android") == locator.for_platform("ios") == (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN")


def test_capabilities_expand_env_and_resolve_app_path(monkeypatch):
    monkeypatch.setenv("ANDROID_DEVICE_NAME", "Pixel_8_API_34")
    caps = load_capabilities("android")
    assert caps["appium:deviceName"] == "Pixel_8_API_34"
    assert caps["appium:automationName"] == "UiAutomator2"
    # Compare path parts, not raw strings, so the check holds on Windows (\) and POSIX (/).
    assert Path(caps["appium:app"]).parts[-2:] == ("apps", "Android.SauceLabs.Mobile.Sample.app.2.7.1.apk")


def test_unknown_platform_is_rejected():
    with pytest.raises(ValueError):
        load_settings("windows")
