"""Cross-platform locator definition.

A Locator holds one strategy per platform. Page objects declare locators once and the
correct strategy is resolved at runtime from the active platform, so the same page
class serves Android and iOS. Templated values (for example a product name) are filled
with Locator.format(...).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from appium.webdriver.common.appiumby import AppiumBy

Strategy = Tuple[str, str]


@dataclass(frozen=True)
class Locator:
    android: Strategy
    ios: Strategy
    description: str = ""

    @classmethod
    def accessibility_id(cls, value: str, description: str = "") -> "Locator":
        """Use when the app exposes the same accessibility id on both platforms.

        The demo app sets accessibilityLabel on Android and testID on iOS to the same
        value, which Appium maps to the accessibility id strategy on both.
        """
        strategy = (AppiumBy.ACCESSIBILITY_ID, value)
        return cls(android=strategy, ios=strategy, description=description or value)

    def resolve(self, platform: str) -> Strategy:
        if platform == "android":
            return self.android
        if platform == "ios":
            return self.ios
        raise ValueError(f"Unknown platform: {platform}")

    def format(self, **kwargs) -> "Locator":
        return Locator(
            android=(self.android[0], self.android[1].format(**kwargs)),
            ios=(self.ios[0], self.ios[1].format(**kwargs)),
            description=self.description.format(**kwargs),
        )

    def __str__(self) -> str:
        return self.description or f"{self.android} / {self.ios}"
