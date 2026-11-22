from __future__ import annotations

from selenium.common.exceptions import NoSuchElementException

from locators.checkout_locators import CartLocators as C
from pages.base_page import BasePage
from pages.checkout_pages import CheckoutInfoPage


class CartPage(BasePage):
    SCREEN = C.SCREEN

    def contains_item(self, name: str) -> bool:
        locator = C.ITEM_NAME.format(name=name)
        try:
            self.scroll_to(locator)
        except NoSuchElementException:
            return False
        return True

    def checkout(self) -> CheckoutInfoPage:
        self.scroll_to(C.CHECKOUT)
        self.tap(C.CHECKOUT)
        return CheckoutInfoPage(self.driver, self.settings).wait_until_loaded()
