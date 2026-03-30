from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.order_item_schema import OrderItemCreate, OrderItemResponse


class OrderCreateRequest(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderResponse(BaseModel):
    id: str
    user_id: str
    total_amount: float
    status: str
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class SalesReportResponse(BaseModel):
    total_orders: int
    pending_orders: int
    completed_orders: int
    cancelled_orders: int
    gross_revenue: float
    completed_revenue: float
    total_items_sold: int
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
