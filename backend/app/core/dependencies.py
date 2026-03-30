from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.core.database import get_database
from app.core.security import decode_access_token, extract_bearer_token, http_bearer_scheme
from app.exceptions.custom_exceptions import ForbiddenException, UnauthorizedException
from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.utils.constants import ROLE_ADMIN, ROLE_CUSTOMER


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_scheme),
    database=Depends(get_database),
) -> UserModel:
    token = extract_bearer_token(credentials)
    payload = decode_access_token(token)
    user_repository = UserRepository(database)
    user = await user_repository.get_by_id(payload.sub)
    if user is None:
        raise UnauthorizedException("User for the supplied token was not found.")
    return user


async def require_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != ROLE_ADMIN:
        raise ForbiddenException("Admin access is required.")
    return current_user


async def require_customer(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != ROLE_CUSTOMER:
        raise ForbiddenException("Customer access is required.")
    return current_user
