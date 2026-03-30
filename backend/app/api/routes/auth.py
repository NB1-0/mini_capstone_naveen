from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from app.controllers import auth_controller
from app.core.dependencies import get_current_user
from app.exceptions.custom_exceptions import BadRequestException
from app.models.user_model import UserModel
from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user_schema import UserResponse
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return await auth_controller.register(payload, service)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return await auth_controller.login(payload, service)


@router.post("/token", response_model=TokenResponse)
async def token(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        raise BadRequestException("username and password are required.")

    auth_response = await auth_controller.token_login(username, password, service)
    return TokenResponse(access_token=auth_response.access_token, token_type=auth_response.token_type)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: UserModel = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return await auth_controller.get_profile(current_user, service)
