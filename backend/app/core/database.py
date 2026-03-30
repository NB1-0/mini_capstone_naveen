from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING

from app.core.config import get_settings
from app.db.mongo_client import create_mongo_client
from app.utils.constants import (
    BOOKS_COLLECTION,
    ORDERS_COLLECTION,
    ORDER_ITEMS_COLLECTION,
    USERS_COLLECTION,
)


class DatabaseManager:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None
        self.database: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        if self.database is not None:
            return

        settings = get_settings()
        self.client = create_mongo_client(settings.mongodb_url)
        self.database = self.client[settings.mongodb_db_name]
        await self.database.command("ping")
        await self._ensure_indexes()

    async def disconnect(self) -> None:
        if self.client is not None:
            self.client.close()
        self.client = None
        self.database = None

    async def _ensure_indexes(self) -> None:
        if self.database is None:
            return

        await self.database[USERS_COLLECTION].create_index([("email", ASCENDING)], unique=True)
        await self.database[ORDERS_COLLECTION].create_index([("user_id", ASCENDING)])
        await self.database[ORDER_ITEMS_COLLECTION].create_index([("order_id", ASCENDING)])
        await self.database[ORDER_ITEMS_COLLECTION].create_index([("book_id", ASCENDING)])
        await self.database[BOOKS_COLLECTION].create_index([("title", ASCENDING)])


database_manager = DatabaseManager()


def get_database() -> AsyncIOMotorDatabase:
    if database_manager.database is None:
        raise RuntimeError("Database connection has not been initialized.")
    return database_manager.database
