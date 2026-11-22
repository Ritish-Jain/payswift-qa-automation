"""Touch gestures built on W3C pointer actions, which both UiAutomator2 and XCUITest support.

Using W3C actions (instead of mobile: scroll or UiScrollable) keeps one implementation
for both platforms.
"""
from __future__ import annotations

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from framework.locator import Locator
from framework.waits import Waits


class Gestures:
    SWIPE_DURATION_MS = 600

    def __init__(self, driver, waits: Waits, max_swipes: int):
        self.driver = driver
        self.waits = waits
        self.max_swipes = max_swipes

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        finger = PointerInput(interaction.POINTER_TOUCH, "finger")
        actions = ActionBuilder(self.driver, mouse=finger, duration=self.SWIPE_DURATION_MS)
        actions.pointer_action.move_to_location(start_x, start_y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.move_to_location(end_x, end_y)
        actions.pointer_action.release()
        actions.perform()

    def swipe_up(self) -> None:
        """Finger moves up, content scrolls down (reveals items lower in the list)."""
        size = self.driver.get_window_size()
        x = size["width"] // 2
        self.swipe(x, int(size["height"] * 0.75), x, int(size["height"] * 0.30))

    def swipe_down(self) -> None:
        size = self.driver.get_window_size()
        x = size["width"] // 2
        self.swipe(x, int(size["height"] * 0.30), x, int(size["height"] * 0.75))

    def swipe_until_visible(self, target: Locator, list_items: Locator | None = None) -> None:
        """Swipe up until target is on screen.

        Stops early and fails if a swipe no longer changes what is visible, which means
        we hit the end of the list. list_items is any locator whose texts change as
        the list scrolls (for example item titles); without it we compare page source.
        """
        last_seen = None
        for _ in range(self.max_swipes):
            if self.waits.is_visible(target):
                return
            visible_now = self._get_visible_items(list_items)
            if visible_now == last_seen:
                break
            last_seen = visible_now
            self.swipe_up()
        if self.waits.is_visible(target):
            return
        raise NoSuchElementException(
            f"'{target}' not found after scrolling (max {self.max_swipes} swipes or end of list)."
        )

    def _get_visible_items(self, list_items: Locator | None):
        if list_items is None:
            return self.driver.page_source
        strategy = list_items.resolve(self.waits.platform)
        return tuple(el.text for el in self.driver.find_elements(*strategy))
