from __future__ import annotations

from app.models.base_model import MongoDocumentModel


class UserModel(MongoDocumentModel):
    email: str
    password: str
    role: str
