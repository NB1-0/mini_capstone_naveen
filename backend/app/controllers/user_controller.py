from __future__ import annotations

from app.models.user_model import UserModel
from app.schemas.user_schema import UserResponse
from app.services.user_service import UserService


async def get_me(current_user: UserModel, service: UserService) -> UserResponse:
    return await service.get_current_user(current_user)


async def list_users(service: UserService) -> list[UserResponse]:
    return await service.list_users()
