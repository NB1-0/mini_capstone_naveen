from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.exceptions.custom_exceptions import BadRequestException


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def serialize_mongo_document(document: dict[str, Any] | None) -> dict[str, Any] | None:
    if document is None:
        return None

    serialized = dict(document)
    serialized["id"] = str(serialized.pop("_id"))
    return serialized


def serialize_many_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [serialize_mongo_document(document) for document in documents if document is not None]


def parse_object_id(value: str, label: str = "resource id") -> ObjectId:
    if not ObjectId.is_valid(value):
        raise BadRequestException(f"Invalid {label}.")
    return ObjectId(value)
