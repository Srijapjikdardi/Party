"""
Test setup: a dedicated `partype_test` Postgres database, migrated
with real Alembic (not create_all — exercises the same migration path
production uses), truncated between tests for isolation.

Env vars are set before any `app.*` import because Settings/engine are
constructed at import time (see app/core/config.py, app/db/session.py)
— conftest.py is always imported before test modules, so this is the
one place that ordering is guaranteed.
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEST_DB_NAME = "partype_test"
TEST_DB_URL = f"postgresql+psycopg://postgres:postgres@localhost:5432/{TEST_DB_NAME}"

os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["SECRET_KEY"] = "test-only-secret-key-not-for-production-0123456789abcdef"
os.environ["ENVIRONMENT"] = "test"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["MAX_FAILED_LOGIN_ATTEMPTS"] = "5"
os.environ["ACCOUNT_LOCKOUT_MINUTES"] = "15"

sys.path.insert(0, str(BACKEND_DIR))

import psycopg  # noqa: E402
import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, text  # noqa: E402


def _recreate_test_database() -> None:
    conn = psycopg.connect(
        "postgresql://postgres:postgres@localhost:5432/postgres", autocommit=True
    )
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
        cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def _migrated_test_database():
    _recreate_test_database()
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(alembic_cfg, "head")
    yield


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _clean_tables(_migrated_test_database):
    """Truncate every app table before each test — schema stays, data doesn't."""
    from app.db.session import engine

    with Session(engine) as session:
        tables = [
            "notifications", "wallet_transactions", "password_reset_tokens",
            "email_verification_tokens", "refresh_tokens", "payment_transactions",
            "payments", "bill_split_records", "bills", "order_items", "orders",
            "cart_items", "carts", "session_participants", "dining_sessions",
            "menu_items", "menu_categories", "restaurant_tables", "restaurant_staff",
            "restaurants", "users", "restaurant_roles",
        ]
        for table in tables:
            session.exec(text(f'TRUNCATE TABLE "{table}" CASCADE'))
        session.commit()
    yield
