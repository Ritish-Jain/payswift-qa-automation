"""Base class for all screens. Holds the driver, waits and gestures, and the small set of
element interactions every page needs. Page objects never assert; they return state
and the tests decide what is correct.
"""
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
        self.waits = Waits(driver, settings.platform, settings.explicit_wait_seconds)
        self.gestures = Gestures(driver, self.waits, settings.max_scroll_attempts)

    # ---- screen state -------------------------------------------------------------
    def wait_until_loaded(self):
        if self.SCREEN is not None:
            self.waits.visible(self.SCREEN)
        return self

    def is_displayed(self) -> bool:
        return self.SCREEN is not None and self.waits.is_visible_now(self.SCREEN)

    # ---- element actions ----------------------------------------------------------
    def tap(self, locator: Locator) -> None:
        self.waits.clickable(locator).click()

    def type_text(self, locator: Locator, text: str) -> None:
        element = self.waits.visible(locator)
        element.clear()
        if text:
            element.send_keys(text)

    def text_of(self, locator: Locator) -> str:
        return self.waits.visible(locator).text

    def texts_of(self, locator: Locator) -> list[str]:
        return [el.text for el in self.waits.all_present(locator)]

    def scroll_to(self, locator: Locator, list_marker: Locator | None = None) -> None:
        self.gestures.scroll_until_visible(locator, list_marker)

    def hide_keyboard_if_shown(self) -> None:
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()
