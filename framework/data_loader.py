"""Reads JSON files from test_data/. Numbers are loaded as Decimal."""
from __future__ import annotations

import json
from decimal import Decimal
from functools import lru_cache

from framework.config import PROJECT_ROOT

TEST_DATA_DIR = PROJECT_ROOT / "test_data"


@lru_cache(maxsize=None)
def load_test_data(name: str) -> dict:
    path = TEST_DATA_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f, parse_float=Decimal)
