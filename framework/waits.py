"""Explicit waits. No time.sleep() in this project."""
from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from framework.locator import Locator


class Waits:
    def __init__(self, driver, platform: str, timeout: float):
        self.driver = driver
        self.platform = platform
        self.timeout = timeout

    def _get_wait(self, timeout: float | None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout if timeout is not None else self.timeout, poll_frequency=0.25)

    def wait_for_visible(self, locator: Locator, timeout: float | None = None) -> WebElement:
        strategy = locator.resolve(self.platform)
        try:
            return self._get_wait(timeout).until(EC.visibility_of_element_located(strategy))
        except TimeoutException as exc:
            raise TimeoutException(f"Element not visible: {locator} using {strategy}") from exc

    def wait_for_clickable(self, locator: Locator, timeout: float | None = None) -> WebElement:
        strategy = locator.resolve(self.platform)
        try:
            return self._get_wait(timeout).until(EC.element_to_be_clickable(strategy))
        except TimeoutException as exc:
            raise TimeoutException(f"Element not clickable: {locator} using {strategy}") from exc

    def wait_for_all(self, locator: Locator, timeout: float | None = None) -> list[WebElement]:
        strategy = locator.resolve(self.platform)
        try:
            return self._get_wait(timeout).until(EC.presence_of_all_elements_located(strategy))
        except TimeoutException as exc:
            raise TimeoutException(f"No elements found: {locator} using {strategy}") from exc

    def is_visible(self, locator: Locator) -> bool:
        """Checks right now, no waiting."""
        elements = self.driver.find_elements(*locator.resolve(self.platform))
        return any(el.is_displayed() for el in elements)
