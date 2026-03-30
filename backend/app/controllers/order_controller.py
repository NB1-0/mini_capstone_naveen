from __future__ import annotations

from app.schemas.order_schema import OrderCreateRequest, OrderResponse
from app.services.order_service import OrderService


async def create_order(user_id: str, payload: OrderCreateRequest, service: OrderService) -> OrderResponse:
    return await service.create_order(user_id, payload)


async def list_orders(user_id: str, service: OrderService) -> list[OrderResponse]:
    return await service.list_user_orders(user_id)


async def get_order(order_id: str, user_id: str, service: OrderService) -> OrderResponse:
    return await service.get_user_order(user_id, order_id)
