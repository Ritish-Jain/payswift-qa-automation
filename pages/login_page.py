from __future__ import annotations

from locators.login_locators import LoginLocators as L
from pages.base_page import BasePage
from pages.products_page import ProductsPage


class LoginPage(BasePage):
    SCREEN = L.LOGIN_BUTTON

    def enter_credentials(self, username: str, password: str) -> "LoginPage":
        self.type_text(L.USERNAME, username)
        self.type_text(L.PASSWORD, password)
        self.hide_keyboard_if_shown()
        return self

    def submit(self) -> None:
        self.tap(L.LOGIN_BUTTON)

    def login_as(self, username: str, password: str) -> ProductsPage:
        self.enter_credentials(username, password).submit()
        return ProductsPage(self.driver, self.settings).wait_until_loaded()

    def attempt_login(self, username: str, password: str) -> "LoginPage":
        """Submit credentials that are expected to be rejected; stay on this page."""
        self.enter_credentials(username, password).submit()
        return self

    def error_message(self) -> str:
        return self.text_of(L.ERROR_MESSAGE)
