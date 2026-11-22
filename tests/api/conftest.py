from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import requests

from framework.data_loader import load_test_data

SCHEMA_DIR = Path(__file__).parent / "schemas"


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("API_BASE_URL", "https://jsonplaceholder.typicode.com").rstrip("/")


@pytest.fixture(scope="session")
def session():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json; charset=UTF-8", "Accept": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="session")
def transfer_data() -> dict:
    return load_test_data("api_transfer")


@pytest.fixture(scope="session")
def schema() -> dict:
    return json.loads((SCHEMA_DIR / "transfer_initiate_response.schema.json").read_text(encoding="utf-8"))
