from __future__ import annotations

from app.models.base_model import MongoDocumentModel


class OrderModel(MongoDocumentModel):
    user_id: str
    total_amount: float
    status: str
