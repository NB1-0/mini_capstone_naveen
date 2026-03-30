from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient


def create_mongo_client(mongodb_url: str) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(mongodb_url)
