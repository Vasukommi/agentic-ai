import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

APP_ROOT = Path(__file__).resolve().parents[1]
TEST_DB_PATH = Path(__file__).resolve().parent / "test_agentic_ai.db"

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

os.environ["AGENTIC_DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["AGENTIC_AUTO_CREATE_TABLES"] = "true"
os.environ.setdefault("AGENTIC_ENVIRONMENT", "test")


@pytest.fixture(autouse=True)
def clear_settings_cache():
    from app.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def client():
    from app.db.session import engine
    from app.main import app

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    with TestClient(app) as test_client:
        yield test_client

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
