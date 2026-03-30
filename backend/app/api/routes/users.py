from __future__ import annotations

from fastapi import APIRouter, Depends

from app.controllers import user_controller
from app.core.dependencies import get_current_user, require_admin
from app.models.user_model import UserModel
from app.schemas.user_schema import UserResponse
from app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserModel = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await user_controller.get_me(current_user, service)


@router.get("", response_model=list[UserResponse])
async def list_users(
    _: UserModel = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    return await user_controller.list_users(service)
