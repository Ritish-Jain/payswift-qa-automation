"""Creates an Appium session for the requested platform.

Tests and page objects never import platform-specific option classes. They ask the
factory for a driver, and the factory picks UiAutomator2 or XCUITest from the settings.
"""
from __future__ import annotations

import logging

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

from framework.config import Settings, load_capabilities

log = logging.getLogger(__name__)

_OPTIONS_BY_PLATFORM = {
    "android": UiAutomator2Options,
    "ios": XCUITestOptions,
}


def create_driver(settings: Settings) -> webdriver.Remote:
    caps = load_capabilities(settings.platform)
    options = _OPTIONS_BY_PLATFORM[settings.platform]().load_capabilities(caps)
    log.info("Starting %s session on %s", settings.platform, settings.appium_server_url)
    driver = webdriver.Remote(settings.appium_server_url, options=options)
    # Implicit waits are disabled on purpose: mixing them with explicit waits makes
    # timeouts unpredictable. All synchronisation goes through framework.waits.
    driver.implicitly_wait(0)
    return driver
