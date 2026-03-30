from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user_schema import UserResponse
from app.utils.constants import ROLE_ADMIN, ROLE_CUSTOMER


class UserRole(str, Enum):
    admin = ROLE_ADMIN
    customer = ROLE_CUSTOMER


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = Field(
        default=UserRole.customer,
        description="Role assigned to the user account.",
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
