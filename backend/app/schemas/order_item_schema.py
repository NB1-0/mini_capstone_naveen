from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    book_id: str
    quantity: int = Field(ge=1)


class OrderItemResponse(BaseModel):
    id: str
    order_id: str
    book_id: str
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)
