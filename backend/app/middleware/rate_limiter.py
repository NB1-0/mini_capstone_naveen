from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.exceptions.custom_exceptions import RateLimitExceededException


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int, window_seconds: int) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in {"/docs", "/redoc", "/openapi.json", "/health"}:
            return await call_next(request)

        client_host = request.client.host if request.client else "anonymous"
        cache_key = f"{client_host}:{request.url.path}"
        now = time.monotonic()
        valid_after = now - self.window_seconds

        window = [stamp for stamp in self._requests.get(cache_key, []) if stamp > valid_after]
        if len(window) >= self.max_requests:
            raise RateLimitExceededException()

        window.append(now)
        self._requests[cache_key] = window
        return await call_next(request)
