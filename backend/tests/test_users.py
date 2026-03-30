from __future__ import annotations

import pytest

from app.core.dependencies import get_current_user, require_admin
from app.schemas.user_schema import UserResponse
from app.services.user_service import get_user_service
from tests.conftest import app, build_user

pytestmark = pytest.mark.asyncio


class FakeUserService:
    async def get_current_user(self, current_user):
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role,
            created_at=current_user.created_at,
        )

    async def list_users(self):
        return [
            UserResponse(
                id="admin-1",
                email="admin@example.com",
                role="admin",
                created_at=build_user("admin-1", "admin@example.com", "admin").created_at,
            )
        ]


async def test_get_me(client):
    app.dependency_overrides[get_user_service] = lambda: FakeUserService()
    app.dependency_overrides[get_current_user] = lambda: build_user("user-1", "user@example.com", "customer")

    response = await client.get("/api/v1/users/me", headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


async def test_list_users_admin_only(client):
    app.dependency_overrides[get_user_service] = lambda: FakeUserService()
    app.dependency_overrides[require_admin] = lambda: build_user("admin-1", "admin@example.com", "admin")

    response = await client.get("/api/v1/users", headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json()[0]["role"] == "admin"
