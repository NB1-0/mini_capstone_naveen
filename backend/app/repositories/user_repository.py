from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user_model import UserModel
from app.utils.constants import USERS_COLLECTION
from app.utils.helpers import parse_object_id, serialize_mongo_document


class UserRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database[USERS_COLLECTION]

    async def create_user(self, payload: dict) -> UserModel:
        result = await self.collection.insert_one(payload)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return UserModel.model_validate(serialize_mongo_document(document))

    async def get_by_email(self, email: str) -> UserModel | None:
        document = await self.collection.find_one({"email": email.lower()})
        serialized = serialize_mongo_document(document)
        return UserModel.model_validate(serialized) if serialized else None

    async def get_by_id(self, user_id: str) -> UserModel | None:
        document = await self.collection.find_one({"_id": parse_object_id(user_id, "user id")})
        serialized = serialize_mongo_document(document)
        return UserModel.model_validate(serialized) if serialized else None

    async def list_users(self) -> list[UserModel]:
        documents = await self.collection.find().sort("created_at", -1).to_list(length=None)
        return [
            UserModel.model_validate(serialized)
            for serialized in map(serialize_mongo_document, documents)
            if serialized is not None
        ]
