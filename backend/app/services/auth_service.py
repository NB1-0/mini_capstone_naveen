from __future__ import annotations

from fastapi import Depends

from app.core.database import get_database
from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.custom_exceptions import ConflictException, UnauthorizedException
from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.user_schema import UserResponse
from app.utils.helpers import utc_now


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def register_user(self, payload: RegisterRequest) -> AuthResponse:
        existing_user = await self.user_repository.get_by_email(payload.email)
        if existing_user is not None:
            raise ConflictException("An account with this email already exists.")

        user = await self.user_repository.create_user(
            {
                "email": payload.email.lower(),
                "password": hash_password(payload.password),
                "role": payload.role.value,
                "created_at": utc_now(),
            }
        )
        return self._build_auth_response(user)

    async def login_user(self, payload: LoginRequest) -> AuthResponse:
        return await self.login_with_credentials(payload.email, payload.password)

    async def login_with_credentials(self, email: str, password: str) -> AuthResponse:
        user = await self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.password):
            raise UnauthorizedException("Invalid email or password.")
        return self._build_auth_response(user)

    async def get_profile(self, current_user: UserModel) -> UserResponse:
        return self._build_user_response(current_user)

    def _build_auth_response(self, user: UserModel) -> AuthResponse:
        token = create_access_token(subject=user.id, role=user.role)
        return AuthResponse(access_token=token, user=self._build_user_response(user))

    @staticmethod
    def _build_user_response(user: UserModel) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )


def get_auth_service(database=Depends(get_database)) -> AuthService:
    return AuthService(UserRepository(database))
