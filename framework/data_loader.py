"""Loads externalised test data from the test_data/ folder.

Decimal is used for every JSON number so prices and amounts keep their exact value.
"""
from __future__ import annotations

import json
from decimal import Decimal
from functools import lru_cache

from framework.config import PROJECT_ROOT

TEST_DATA_DIR = PROJECT_ROOT / "test_data"


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    path = TEST_DATA_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as fh:
        return json.load(fh, parse_float=Decimal)
