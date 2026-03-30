from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.models.order_model import OrderModel
from app.utils.constants import ORDERS_COLLECTION
from app.utils.helpers import parse_object_id, serialize_mongo_document


class OrderRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database[ORDERS_COLLECTION]

    async def create_order(self, payload: dict) -> OrderModel:
        result = await self.collection.insert_one(payload)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return OrderModel.model_validate(serialize_mongo_document(document))

    async def get_by_id(self, order_id: str) -> OrderModel | None:
        document = await self.collection.find_one({"_id": parse_object_id(order_id, "order id")})
        serialized = serialize_mongo_document(document)
        return OrderModel.model_validate(serialized) if serialized else None

    async def list_orders(self) -> list[OrderModel]:
        documents = await self.collection.find().sort("created_at", -1).to_list(length=None)
        return [
            OrderModel.model_validate(serialized)
            for serialized in map(serialize_mongo_document, documents)
            if serialized is not None
        ]

    async def list_by_user_id(self, user_id: str) -> list[OrderModel]:
        documents = await self.collection.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        return [
            OrderModel.model_validate(serialized)
            for serialized in map(serialize_mongo_document, documents)
            if serialized is not None
        ]

    async def update_status(self, order_id: str, status: str) -> OrderModel | None:
        document = await self.collection.find_one_and_update(
            {"_id": parse_object_id(order_id, "order id")},
            {"$set": {"status": status}},
            return_document=ReturnDocument.AFTER,
        )
        serialized = serialize_mongo_document(document)
        return OrderModel.model_validate(serialized) if serialized else None

    async def delete_order(self, order_id: str) -> bool:
        result = await self.collection.delete_one({"_id": parse_object_id(order_id, "order id")})
        return result.deleted_count == 1
