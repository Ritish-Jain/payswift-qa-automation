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
    raw_text: dict


class CheckoutInfoPage(BasePage):
    SCREEN = Info.SCREEN

    def fill_details(self, first_name: str, last_name: str, postal_code: str) -> "CheckoutInfoPage":
        self.enter_text(Info.FIRST_NAME, first_name)
        self.enter_text(Info.LAST_NAME, last_name)
        self.enter_text(Info.POSTAL_CODE, postal_code)
        self.hide_keyboard()
        return self

    def click_continue(self) -> "CheckoutOverviewPage":
        self.click(Info.CONTINUE)
        return CheckoutOverviewPage(self.driver, self.settings).wait_for_page()

    def continue_and_get_error(self) -> str:
        self.click(Info.CONTINUE)
        return self.get_text(Info.ERROR_MESSAGE)


class CheckoutOverviewPage(BasePage):
    SCREEN = Overview.SCREEN

    def get_order_summary(self) -> OrderSummary:
        self.scroll_to(Overview.TOTAL)
        raw_text = {
            "item_total": self.get_text(Overview.ITEM_TOTAL),
            "tax": self.get_text(Overview.TAX),
            "total": self.get_text(Overview.TOTAL),
        }
        return OrderSummary(
            item_total=parse_amount(raw_text["item_total"]),
            tax=parse_amount(raw_text["tax"]),
            total=parse_amount(raw_text["total"]),
            raw_text=raw_text,
        )

    def click_finish(self) -> "CheckoutCompletePage":
        self.scroll_to(Overview.FINISH)
        self.click(Overview.FINISH)
        return CheckoutCompletePage(self.driver, self.settings).wait_for_page()


class CheckoutCompletePage(BasePage):
    SCREEN = Done.SCREEN

    def is_order_confirmed(self, header_text: str) -> bool:
        try:
            self.waits.wait_for_visible(Done.CONFIRMATION_HEADER.format(text=header_text))
        except TimeoutException:
            return False
        return True
