from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import admin, auth, books, orders, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(books.router)
api_router.include_router(orders.router)
api_router.include_router(admin.router)
