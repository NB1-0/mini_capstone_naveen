from __future__ import annotations

from fastapi import status


class AppException(Exception):
    def __init__(self, detail: str, status_code: int) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request.") -> None:
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Authentication required.") -> None:
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "You do not have permission to perform this action.") -> None:
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found.") -> None:
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists.") -> None:
        super().__init__(detail, status.HTTP_409_CONFLICT)


class RateLimitExceededException(AppException):
    def __init__(self, detail: str = "Rate limit exceeded. Please try again later.") -> None:
        super().__init__(detail, status.HTTP_429_TOO_MANY_REQUESTS)
