from __future__ import annotations

from locators.products_locators import ProductDetailLocators as D
from locators.products_locators import ProductsLocators as P
from pages.base_page import BasePage


class ProductsPage(BasePage):
    SCREEN = P.SCREEN

    def scroll_to_product(self, name: str) -> "ProductsPage":
        self.scroll_to(P.PRODUCT_TITLE.format(name=name), list_items=P.PRODUCT_TITLES)
        return self

    def open_product(self, name: str) -> "ProductDetailPage":
        self.scroll_to_product(name)
        self.click(P.PRODUCT_TITLE.format(name=name))
        return ProductDetailPage(self.driver, self.settings).wait_for_page()

    def add_product_to_cart(self, name: str) -> "ProductsPage":
        """Add from the detail page (simpler than finding the button inside the list card)."""
        self.open_product(name).add_to_cart().go_back()
        return self

    def open_cart(self):
        from pages.cart_page import CartPage

        self.click(P.CART_ICON)
        return CartPage(self.driver, self.settings).wait_for_page()


class ProductDetailPage(BasePage):
    SCREEN = D.SCREEN

    def get_name_and_description(self) -> tuple[str, str]:
        texts = self.get_texts(D.DETAIL_TEXTS)
        name = texts[0] if texts else ""
        description = texts[1] if len(texts) > 1 else ""
        return name, description

    def get_price(self) -> str:
        self.scroll_to(D.PRICE)
        return self.get_text(D.PRICE)

    def add_to_cart(self) -> "ProductDetailPage":
        self.scroll_to(D.ADD_TO_CART)
        self.click(D.ADD_TO_CART)
        self.waits.wait_for_visible(D.REMOVE)  # button changes to REMOVE when added
        return self

    def go_back(self) -> ProductsPage:
        self.click(D.BACK_TO_PRODUCTS)
        return ProductsPage(self.driver, self.settings).wait_for_page()
