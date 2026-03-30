from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.models.book_model import BookModel
from app.utils.constants import BOOKS_COLLECTION
from app.utils.helpers import parse_object_id, serialize_mongo_document


class BookRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database[BOOKS_COLLECTION]

    async def list_books(self) -> list[BookModel]:
        documents = await self.collection.find().sort("created_at", -1).to_list(length=None)
        return [
            BookModel.model_validate(serialized)
            for serialized in map(serialize_mongo_document, documents)
            if serialized is not None
        ]

    async def get_by_id(self, book_id: str) -> BookModel | None:
        document = await self.collection.find_one({"_id": parse_object_id(book_id, "book id")})
        serialized = serialize_mongo_document(document)
        return BookModel.model_validate(serialized) if serialized else None

    async def create_book(self, payload: dict) -> BookModel:
        result = await self.collection.insert_one(payload)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return BookModel.model_validate(serialize_mongo_document(document))

    async def update_book(self, book_id: str, payload: dict) -> BookModel | None:
        document = await self.collection.find_one_and_update(
            {"_id": parse_object_id(book_id, "book id")},
            {"$set": payload},
            return_document=ReturnDocument.AFTER,
        )
        serialized = serialize_mongo_document(document)
        return BookModel.model_validate(serialized) if serialized else None

    async def delete_book(self, book_id: str) -> bool:
        result = await self.collection.delete_one({"_id": parse_object_id(book_id, "book id")})
        return result.deleted_count == 1

    async def adjust_stock(self, book_id: str, delta: int) -> BookModel | None:
        filter_query: dict = {"_id": parse_object_id(book_id, "book id")}
        if delta < 0:
            filter_query["stock"] = {"$gte": abs(delta)}

        document = await self.collection.find_one_and_update(
            filter_query,
            {"$inc": {"stock": delta}},
            return_document=ReturnDocument.AFTER,
        )
        serialized = serialize_mongo_document(document)
        return BookModel.model_validate(serialized) if serialized else None
