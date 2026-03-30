from __future__ import annotations

from collections import defaultdict

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.order_item_model import OrderItemModel
from app.utils.constants import ORDER_ITEMS_COLLECTION
from app.utils.helpers import parse_object_id, serialize_mongo_document


class OrderItemRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database[ORDER_ITEMS_COLLECTION]

    async def create_many(self, payload: list[dict]) -> list[OrderItemModel]:
        if not payload:
            return []

        result = await self.collection.insert_many(payload)
        documents = await self.collection.find({"_id": {"$in": result.inserted_ids}}).to_list(length=None)
        return [
            OrderItemModel.model_validate(serialized)
            for serialized in map(serialize_mongo_document, documents)
            if serialized is not None
        ]

    async def list_by_order_id(self, order_id: str) -> list[OrderItemModel]:
        documents = await self.collection.find({"order_id": order_id}).to_list(length=None)
        return [
            OrderItemModel.model_validate(serialized)
            for serialized in map(serialize_mongo_document, documents)
            if serialized is not None
        ]

    async def list_by_order_ids(self, order_ids: list[str]) -> dict[str, list[OrderItemModel]]:
        if not order_ids:
            return {}

        documents = await self.collection.find({"order_id": {"$in": order_ids}}).to_list(length=None)
        grouped_items: dict[str, list[OrderItemModel]] = defaultdict(list)
        for serialized in map(serialize_mongo_document, documents):
            if serialized is None:
                continue
            item = OrderItemModel.model_validate(serialized)
            grouped_items[item.order_id].append(item)
        return dict(grouped_items)

    async def delete_many_by_order_id(self, order_id: str) -> None:
        await self.collection.delete_many({"order_id": order_id})

    async def get_by_id(self, order_item_id: str) -> OrderItemModel | None:
        document = await self.collection.find_one({"_id": parse_object_id(order_item_id, "order item id")})
        serialized = serialize_mongo_document(document)
        return OrderItemModel.model_validate(serialized) if serialized else None
