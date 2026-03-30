from __future__ import annotations

from fastapi import Depends

from app.core.database import get_database
from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserResponse


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def get_current_user(self, current_user: UserModel) -> UserResponse:
        return self._build_user_response(current_user)

    async def list_users(self) -> list[UserResponse]:
        users = await self.user_repository.list_users()
        return [self._build_user_response(user) for user in users]

    @staticmethod
    def _build_user_response(user: UserModel) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )


def get_user_service(database=Depends(get_database)) -> UserService:
    return UserService(UserRepository(database))
