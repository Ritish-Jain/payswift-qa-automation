"""Common actions for all pages. No asserts in page objects, only in tests."""
from __future__ import annotations

from framework.config import Settings
from framework.gestures import Gestures
from framework.locator import Locator
from framework.waits import Waits


class BasePage:
    SCREEN: Locator | None = None

    def __init__(self, driver, settings: Settings):
        self.driver = driver
        self.settings = settings
        self.waits = Waits(driver, settings.platform, settings.wait_timeout)
        self.gestures = Gestures(driver, self.waits, settings.max_swipes)

    def wait_for_page(self):
        if self.SCREEN is not None:
            self.waits.wait_for_visible(self.SCREEN)
        return self

    def is_displayed(self) -> bool:
        return self.SCREEN is not None and self.waits.is_visible(self.SCREEN)

    def click(self, locator: Locator) -> None:
        self.waits.wait_for_clickable(locator).click()

    def enter_text(self, locator: Locator, text: str) -> None:
        element = self.waits.wait_for_visible(locator)
        element.clear()
        if text:
            element.send_keys(text)

    def get_text(self, locator: Locator) -> str:
        return self.waits.wait_for_visible(locator).text

    def get_texts(self, locator: Locator) -> list[str]:
        return [el.text for el in self.waits.wait_for_all(locator)]

    def scroll_to(self, locator: Locator, list_items: Locator | None = None) -> None:
        self.gestures.swipe_until_visible(locator, list_items)

    def hide_keyboard(self) -> None:
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()
