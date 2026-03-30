from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.controllers import admin_controller
from app.core.dependencies import require_admin
from app.models.user_model import UserModel
from app.schemas.order_schema import OrderResponse, SalesReportResponse
from app.services.order_service import OrderService, get_order_service

router = APIRouter(prefix="/admin", tags=["Admin"])


class UpdateOrderStatusRequest(BaseModel):
    status: str


@router.get("/orders", response_model=list[OrderResponse])
async def list_all_orders(
    _: UserModel = Depends(require_admin),
    service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    return await admin_controller.list_all_orders(service)


@router.get("/salesreport", response_model=SalesReportResponse)
async def sales_report(
    _: UserModel = Depends(require_admin),
    service: OrderService = Depends(get_order_service),
) -> SalesReportResponse:
    return await admin_controller.get_sales_report(service)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    payload: UpdateOrderStatusRequest,
    _: UserModel = Depends(require_admin),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await admin_controller.update_order_status(order_id, payload.status, service)
