from __future__ import annotations

from locators.login_locators import LoginLocators as L
from pages.base_page import BasePage
from pages.products_page import ProductsPage


class LoginPage(BasePage):
    SCREEN = L.LOGIN_BUTTON

    def enter_credentials(self, username: str, password: str) -> "LoginPage":
        self.enter_text(L.USERNAME, username)
        self.enter_text(L.PASSWORD, password)
        self.hide_keyboard()
        return self

    def click_login(self) -> None:
        self.click(L.LOGIN_BUTTON)

    def login(self, username: str, password: str) -> ProductsPage:
        self.enter_credentials(username, password).click_login()
        return ProductsPage(self.driver, self.settings).wait_for_page()

    def try_login(self, username: str, password: str) -> "LoginPage":
        """Submit credentials that are expected to be rejected; stay on this page."""
        self.enter_credentials(username, password).click_login()
        return self

    def get_error_message(self) -> str:
        return self.get_text(L.ERROR_MESSAGE)
