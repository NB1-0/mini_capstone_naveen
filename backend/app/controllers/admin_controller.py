from __future__ import annotations

from app.schemas.order_schema import OrderResponse, SalesReportResponse
from app.services.order_service import OrderService


async def list_all_orders(service: OrderService) -> list[OrderResponse]:
    return await service.list_all_orders()


async def get_sales_report(service: OrderService) -> SalesReportResponse:
    return await service.get_sales_report()


async def update_order_status(order_id: str, status: str, service: OrderService) -> OrderResponse:
    return await service.update_order_status(order_id, status)
