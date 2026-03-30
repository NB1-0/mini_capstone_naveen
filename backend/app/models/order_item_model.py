from __future__ import annotations

from app.models.base_model import MongoDocumentModel


class OrderItemModel(MongoDocumentModel):
    order_id: str
    book_id: str
    quantity: int
    price: float
