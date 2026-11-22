from appium.webdriver.common.appiumby import AppiumBy

from framework.locator import Locator


class CartLocators:
    SCREEN = Locator.accessibility_id("test-Cart Content", "Cart screen")
    CHECKOUT = Locator.accessibility_id("test-CHECKOUT", "Checkout button")
    ITEM_NAME = Locator(
        android=(AppiumBy.XPATH, '//*[@content-desc="test-Description"]/android.widget.TextView[@text="{name}"]'),
        ios=(AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeStaticText" AND label == "{name}"'),
        description="Cart item '{name}'",
    )


class CheckoutInfoLocators:
    SCREEN = Locator.accessibility_id("test-Checkout: Your Info", "Checkout information screen")
    FIRST_NAME = Locator.accessibility_id("test-First Name", "First name input")
    LAST_NAME = Locator.accessibility_id("test-Last Name", "Last name input")
    POSTAL_CODE = Locator.accessibility_id("test-Zip/Postal Code", "Postal code input")
    CONTINUE = Locator.accessibility_id("test-CONTINUE", "Continue button")
    ERROR_MESSAGE = Locator(
        android=(AppiumBy.XPATH, '//*[@content-desc="test-Error message"]//android.widget.TextView'),
        ios=(AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "test-Error message"`]/**/XCUIElementTypeStaticText'),
        description="Checkout error message text",
    )


class CheckoutOverviewLocators:
    SCREEN = Locator.accessibility_id("test-CHECKOUT: OVERVIEW", "Checkout overview screen")
    FINISH = Locator.accessibility_id("test-FINISH", "Finish button")

    # Summary labels have no test ids in the app, so they are matched by their prefix.
    _ANDROID_PREFIX = 'new UiSelector().textStartsWith("{prefix}")'
    _IOS_PREFIX = 'type == "XCUIElementTypeStaticText" AND label BEGINSWITH "{prefix}"'

    ITEM_TOTAL = Locator(
        android=(AppiumBy.ANDROID_UIAUTOMATOR, _ANDROID_PREFIX.format(prefix="Item total:")),
        ios=(AppiumBy.IOS_PREDICATE, _IOS_PREFIX.format(prefix="Item total:")),
        description="Item total label",
    )
    TAX = Locator(
        android=(AppiumBy.ANDROID_UIAUTOMATOR, _ANDROID_PREFIX.format(prefix="Tax:")),
        ios=(AppiumBy.IOS_PREDICATE, _IOS_PREFIX.format(prefix="Tax:")),
        description="Tax label",
    )
    TOTAL = Locator(
        android=(AppiumBy.ANDROID_UIAUTOMATOR, _ANDROID_PREFIX.format(prefix="Total:")),
        ios=(AppiumBy.IOS_PREDICATE, _IOS_PREFIX.format(prefix="Total:")),
        description="Order total label",
    )


class CheckoutCompleteLocators:
    SCREEN = Locator.accessibility_id("test-CHECKOUT: COMPLETE!", "Checkout complete screen")
    CONFIRMATION_HEADER = Locator(
        android=(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("{text}")'),
        ios=(AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeStaticText" AND label == "{text}"'),
        description="Confirmation header '{text}'",
    )
