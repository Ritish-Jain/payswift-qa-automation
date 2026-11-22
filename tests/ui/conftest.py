from __future__ import annotations

import pytest

from framework.config import load_settings
from framework.data_loader import load_test_data
from framework.driver_factory import create_driver
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def settings(request):
    return load_settings(request.config.getoption("--platform"))


@pytest.fixture
def driver(settings):
    """A fresh app session per test, so no test depends on state left by another."""
    drv = create_driver(settings)
    yield drv
    drv.quit()


@pytest.fixture
def login_page(driver, settings) -> LoginPage:
    return LoginPage(driver, settings).wait_for_page()


@pytest.fixture
def products_page(login_page):
    user = load_test_data("users")["valid_user"]
    return login_page.login(user["username"], user["password"])
