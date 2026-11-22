"""Runtime settings. Everything environment-specific is read here and nowhere else."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAPABILITIES_FILE = PROJECT_ROOT / "config" / "capabilities.yaml"
REPORTS_DIR = PROJECT_ROOT / "reports"
SUPPORTED_PLATFORMS = ("android", "ios")

_ENV_PATTERN = re.compile(r"\$\{(?P<name>[A-Z0-9_]+)(?::-(?P<default>[^}]*))?\}")


def _expand_env(value):
    """Expand ${VAR} and ${VAR:-default} inside YAML string values."""
    if not isinstance(value, str):
        return value

    def repl(match: re.Match) -> str:
        return os.environ.get(match.group("name"), match.group("default") or "")

    return _ENV_PATTERN.sub(repl, value)


@dataclass(frozen=True)
class Settings:
    platform: str
    appium_server_url: str
    explicit_wait_seconds: float
    max_scroll_attempts: int

    @property
    def is_android(self) -> bool:
        return self.platform == "android"

    @property
    def is_ios(self) -> bool:
        return self.platform == "ios"


def load_settings(platform: str | None = None) -> Settings:
    platform = (platform or os.environ.get("PLATFORM", "android")).lower()
    if platform not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Unsupported platform '{platform}'. Use one of {SUPPORTED_PLATFORMS}.")
    return Settings(
        platform=platform,
        appium_server_url=os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
        explicit_wait_seconds=float(os.environ.get("EXPLICIT_WAIT_SECONDS", "15")),
        max_scroll_attempts=int(os.environ.get("MAX_SCROLL_ATTEMPTS", "8")),
    )


def load_capabilities(platform: str) -> dict:
    with CAPABILITIES_FILE.open(encoding="utf-8") as fh:
        all_caps = yaml.safe_load(fh)
    caps = {key: _expand_env(val) for key, val in all_caps[platform].items()}

    # Resolve a relative app path against the project root so tests run from any cwd.
    app = caps.get("appium:app")
    if app and not app.startswith(("http://", "https://", "/", "storage:", "sauce-storage:")):
        caps["appium:app"] = str((PROJECT_ROOT / app).resolve())
    return caps
