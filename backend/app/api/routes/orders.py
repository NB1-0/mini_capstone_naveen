from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.controllers import order_controller
from app.core.dependencies import require_customer
from app.models.user_model import UserModel
from app.schemas.order_schema import OrderCreateRequest, OrderResponse
from app.services.order_service import OrderService, get_order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    current_user: UserModel = Depends(require_customer),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await order_controller.create_order(current_user.id, payload, service)


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    current_user: UserModel = Depends(require_customer),
    service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    return await order_controller.list_orders(current_user.id, service)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: UserModel = Depends(require_customer),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await order_controller.get_order(order_id, current_user.id, service)
