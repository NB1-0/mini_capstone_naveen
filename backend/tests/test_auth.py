from __future__ import annotations

import pytest

from app.core.dependencies import get_current_user
from app.schemas.auth_schema import AuthResponse
from app.schemas.user_schema import UserResponse
from app.services.auth_service import get_auth_service
from tests.conftest import app, build_user

pytestmark = pytest.mark.asyncio


class FakeAuthService:
    async def register_user(self, payload):
        return AuthResponse(
            access_token="token-register",
            user=UserResponse(
                id="user-1",
                email=payload.email,
                role=payload.role.value,
                created_at=build_user("user-1", payload.email, payload.role.value).created_at,
            ),
        )

    async def login_user(self, payload):
        return AuthResponse(
            access_token="token-login",
            user=UserResponse(
                id="user-1",
                email=payload.email,
                role="customer",
                created_at=build_user("user-1", payload.email, "customer").created_at,
            ),
        )

    async def login_with_credentials(self, email, _password):
        return AuthResponse(
            access_token="token-login",
            user=UserResponse(
                id="user-1",
                email=email,
                role="customer",
                created_at=build_user("user-1", email, "customer").created_at,
            ),
        )

    async def get_profile(self, current_user):
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role,
            created_at=current_user.created_at,
        )


async def test_register(client):
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "customer@example.com", "password": "StrongPass123", "role": "customer"},
    )

    assert response.status_code == 201
    assert response.json()["user"]["email"] == "customer@example.com"
    assert response.json()["user"]["role"] == "customer"


async def test_login(client):
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "customer@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "token-login"


async def test_token_login(client):
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "customer@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


async def test_me(client):
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()
    app.dependency_overrides[get_current_user] = lambda: build_user("user-1", "customer@example.com", "customer")

    response = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json()["role"] == "customer"
