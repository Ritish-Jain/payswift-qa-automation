"""Global pytest hooks: --platform option and screenshot on failure."""
from __future__ import annotations

import re
from datetime import datetime

import pytest

from framework.config import REPORTS_DIR

SCREENSHOT_DIR = REPORTS_DIR / "screenshots"


def pytest_addoption(parser):
    parser.addoption(
        "--platform",
        action="store",
        default=None,
        choices=("android", "ios"),
        help="Target platform for UI tests. Falls back to the PLATFORM env var, then android.",
    )


def _clean_filename(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid)[-150:]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # only for failed UI tests (they have a driver)
    if report.when not in ("setup", "call") or not report.failed:
        return
    driver = item.funcargs.get("driver") if hasattr(item, "funcargs") else None
    if driver is None:
        return

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{_clean_filename(item.nodeid)}_{timestamp}"
    png_path = SCREENSHOT_DIR / f"{base_name}.png"
    xml_path = SCREENSHOT_DIR / f"{base_name}.xml"

    try:
        driver.save_screenshot(str(png_path))
        xml_path.write_text(driver.page_source, encoding="utf-8")
    except Exception as exc:  # session might be gone already, don't hide the real error
        report.sections.append(("failure artefacts", f"Could not capture artefacts: {exc}"))
        return

    report.sections.append(("failure artefacts", f"Screenshot: {png_path}\nPage source: {xml_path}"))

    if item.config.pluginmanager.hasplugin("html"):
        import base64

        import pytest_html

        extras = getattr(report, "extras", [])
        encoded = base64.b64encode(png_path.read_bytes()).decode("ascii")
        extras.append(pytest_html.extras.png(encoded, name="Screenshot on failure"))
        report.extras = extras

    try:
        import allure

        allure.attach.file(str(png_path), name="Screenshot on failure", attachment_type=allure.attachment_type.PNG)
        allure.attach.file(str(xml_path), name="Page source", attachment_type=allure.attachment_type.XML)
    except ImportError:
        pass
