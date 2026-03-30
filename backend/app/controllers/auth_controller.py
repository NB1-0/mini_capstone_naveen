from __future__ import annotations

from app.models.user_model import UserModel
from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.user_schema import UserResponse
from app.services.auth_service import AuthService


async def register(payload: RegisterRequest, service: AuthService) -> AuthResponse:
    return await service.register_user(payload)


async def login(payload: LoginRequest, service: AuthService) -> AuthResponse:
    return await service.login_user(payload)


async def token_login(email: str, password: str, service: AuthService) -> AuthResponse:
    return await service.login_with_credentials(email, password)


async def get_profile(current_user: UserModel, service: AuthService) -> UserResponse:
    return await service.get_profile(current_user)
