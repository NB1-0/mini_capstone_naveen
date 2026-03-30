from __future__ import annotations

from app.models.base_model import MongoDocumentModel


class BookModel(MongoDocumentModel):
    title: str
    author: str
    price: float
    stock: int
