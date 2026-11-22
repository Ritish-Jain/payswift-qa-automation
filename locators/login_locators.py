from appium.webdriver.common.appiumby import AppiumBy

from framework.locator import Locator


class LoginLocators:
    USERNAME = Locator.accessibility_id("test-Username", "Username input")
    PASSWORD = Locator.accessibility_id("test-Password", "Password input")
    LOGIN_BUTTON = Locator.accessibility_id("test-LOGIN", "Login button")

    # test id is on the container, text is in the child
    ERROR_MESSAGE = Locator(
        android=(AppiumBy.XPATH, '//*[@content-desc="test-Error message"]//android.widget.TextView'),
        ios=(AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "test-Error message"`]/**/XCUIElementTypeStaticText'),
        description="Login error message text",
    )
