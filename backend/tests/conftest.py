from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
import sys

import httpx
import pytest
import pytest_asyncio

os.environ["BOOKSTORE_TESTING"] = "true"

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.main import app
from app.models.user_model import UserModel


def build_user(user_id: str, email: str, role: str) -> UserModel:
    return UserModel(
        id=user_id,
        email=email,
        password="hashed-password",
        role=role,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
