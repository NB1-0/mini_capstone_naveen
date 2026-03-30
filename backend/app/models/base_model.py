from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MongoDocumentModel(BaseModel):
    id: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
