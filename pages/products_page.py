from __future__ import annotations

from locators.products_locators import ProductDetailLocators as D
from locators.products_locators import ProductsLocators as P
from pages.base_page import BasePage


class ProductsPage(BasePage):
    SCREEN = P.SCREEN

    def scroll_to_product(self, name: str) -> "ProductsPage":
        self.scroll_to(P.ITEM_TITLE_BY_NAME.format(name=name), list_marker=P.ITEM_TITLES)
        return self

    def open_product(self, name: str) -> "ProductDetailPage":
        self.scroll_to_product(name)
        self.tap(P.ITEM_TITLE_BY_NAME.format(name=name))
        return ProductDetailPage(self.driver, self.settings).wait_until_loaded()

    def add_to_cart(self, name: str) -> "ProductsPage":
        """Adds via the detail screen. This avoids locating a button inside a specific
        list card, which needs different relative locators per platform."""
        self.open_product(name).add_to_cart().back_to_products()
        return self

    def open_cart(self):
        from pages.cart_page import CartPage

        self.tap(P.CART_ICON)
        return CartPage(self.driver, self.settings).wait_until_loaded()


class ProductDetailPage(BasePage):
    SCREEN = D.SCREEN

    def name_and_description(self) -> tuple[str, str]:
        texts = self.texts_of(D.DESCRIPTION_TEXTS)
        name = texts[0] if texts else ""
        description = texts[1] if len(texts) > 1 else ""
        return name, description

    def price_text(self) -> str:
        self.scroll_to(D.PRICE)
        return self.text_of(D.PRICE)

    def add_to_cart(self) -> "ProductDetailPage":
        self.scroll_to(D.ADD_TO_CART)
        self.tap(D.ADD_TO_CART)
        self.waits.visible(D.REMOVE)  # button flips to REMOVE once the cart is updated
        return self

    def back_to_products(self) -> ProductsPage:
        self.tap(D.BACK_TO_PRODUCTS)
        return ProductsPage(self.driver, self.settings).wait_until_loaded()
