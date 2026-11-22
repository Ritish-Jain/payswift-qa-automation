from appium.webdriver.common.appiumby import AppiumBy

from framework.locator import Locator


class ProductsLocators:
    SCREEN = Locator.accessibility_id("test-PRODUCTS", "Products screen")
    CART_ICON = Locator.accessibility_id("test-Cart", "Cart icon")
    PRODUCT_TITLES = Locator.accessibility_id("test-Item title", "All visible product titles")

    # Product title by visible name. Android keeps the name in @text, iOS in label.
    PRODUCT_TITLE = Locator(
        android=(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().description("test-Item title").text("{name}")',
        ),
        ios=(AppiumBy.IOS_PREDICATE, 'name == "test-Item title" AND label == "{name}"'),
        description="Product title '{name}'",
    )


class ProductDetailLocators:
    SCREEN = Locator.accessibility_id("test-Inventory item page", "Product detail screen")
    DETAIL_TEXTS = Locator(
        android=(AppiumBy.XPATH, '//*[@content-desc="test-Description"]/android.widget.TextView'),
        ios=(AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "test-Description"`]/**/XCUIElementTypeStaticText'),
        description="Product name and description texts",
    )
    PRICE = Locator.accessibility_id("test-Price", "Product price")
    ADD_TO_CART = Locator.accessibility_id("test-ADD TO CART", "Add to cart button")
    REMOVE = Locator.accessibility_id("test-REMOVE", "Remove from cart button")
    BACK_TO_PRODUCTS = Locator.accessibility_id("test-BACK TO PRODUCTS", "Back to products")
