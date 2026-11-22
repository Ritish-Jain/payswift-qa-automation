from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from selenium.common.exceptions import TimeoutException

from framework.money import parse_amount
from locators.checkout_locators import CheckoutCompleteLocators as Done
from locators.checkout_locators import CheckoutInfoLocators as Info
from locators.checkout_locators import CheckoutOverviewLocators as Overview
from pages.base_page import BasePage


@dataclass(frozen=True)
class OrderSummary:
    item_total: Decimal
    tax: Decimal
    total: Decimal
    raw: dict


class CheckoutInfoPage(BasePage):
    SCREEN = Info.SCREEN

    def fill(self, first_name: str, last_name: str, postal_code: str) -> "CheckoutInfoPage":
        self.type_text(Info.FIRST_NAME, first_name)
        self.type_text(Info.LAST_NAME, last_name)
        self.type_text(Info.POSTAL_CODE, postal_code)
        self.hide_keyboard_if_shown()
        return self

    def continue_to_overview(self) -> "CheckoutOverviewPage":
        self.tap(Info.CONTINUE)
        return CheckoutOverviewPage(self.driver, self.settings).wait_until_loaded()

    def submit_expecting_error(self) -> str:
        self.tap(Info.CONTINUE)
        return self.text_of(Info.ERROR_MESSAGE)


class CheckoutOverviewPage(BasePage):
    SCREEN = Overview.SCREEN

    def summary(self) -> OrderSummary:
        self.scroll_to(Overview.TOTAL)
        raw = {
            "item_total": self.text_of(Overview.ITEM_TOTAL),
            "tax": self.text_of(Overview.TAX),
            "total": self.text_of(Overview.TOTAL),
        }
        return OrderSummary(
            item_total=parse_amount(raw["item_total"]),
            tax=parse_amount(raw["tax"]),
            total=parse_amount(raw["total"]),
            raw=raw,
        )

    def finish(self) -> "CheckoutCompletePage":
        self.scroll_to(Overview.FINISH)
        self.tap(Overview.FINISH)
        return CheckoutCompletePage(self.driver, self.settings).wait_until_loaded()


class CheckoutCompletePage(BasePage):
    SCREEN = Done.SCREEN

    def shows_confirmation(self, header_text: str) -> bool:
        try:
            self.waits.visible(Done.CONFIRMATION_HEADER.format(text=header_text))
        except TimeoutException:
            return False
        return True
