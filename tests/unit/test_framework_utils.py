"""Unit tests for framework helpers (no device needed)."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from appium.webdriver.common.appiumby import AppiumBy

from framework.config import load_capabilities, load_settings
from framework.locator import Locator
from framework.money import has_two_decimals, parse_amount, round_half_up
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
def test_parse_amount(text, expected):
    assert parse_amount(text) == expected


def test_parse_amount_no_digits():
    with pytest.raises(ValueError):
        parse_amount("Total: $")


@pytest.mark.parametrize(
    "value, expected",
    [(Decimal("3.6784"), Decimal("3.68")), (Decimal("0.005"), Decimal("0.01")), (Decimal("10"), Decimal("10.00"))],
)
def test_round_half_up(value, expected):
    assert round_half_up(value) == expected


def test_two_decimal_check():
    assert has_two_decimals(Decimal("45.98"))
    assert not has_two_decimals(Decimal("59.980000000000004"))


def test_locator_per_platform():
    locator = ProductsLocators.PRODUCT_TITLE.format(name="Sauce Labs Onesie")
    assert locator.resolve("android") == (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().description("test-Item title").text("Sauce Labs Onesie")',
    )
    assert locator.resolve("ios") == (
        AppiumBy.IOS_PREDICATE,
        'name == "test-Item title" AND label == "Sauce Labs Onesie"',
    )


def test_accessibility_id_both_platforms():
    locator = Locator.accessibility_id("test-LOGIN")
    assert locator.resolve("android") == locator.resolve("ios") == (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN")


def test_load_capabilities(monkeypatch):
    monkeypatch.setenv("ANDROID_DEVICE_NAME", "Pixel_8_API_34")
    caps = load_capabilities("android")
    assert caps["appium:deviceName"] == "Pixel_8_API_34"
    assert caps["appium:automationName"] == "UiAutomator2"
    # compare path parts so it works on Windows and Linux/Mac
    assert Path(caps["appium:app"]).parts[-2:] == ("apps", "Android.SauceLabs.Mobile.Sample.app.2.7.1.apk")


def test_invalid_platform():
    with pytest.raises(ValueError):
        load_settings("windows")
