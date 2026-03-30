from __future__ import annotations

from collections import Counter

from fastapi import Depends

from app.core.database import get_database
from app.exceptions.custom_exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.order_model import OrderModel
from app.repositories.book_repository import BookRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order_item_schema import OrderItemResponse
from app.schemas.order_schema import OrderCreateRequest, OrderResponse, SalesReportResponse
from app.utils.constants import (
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_PENDING,
)
from app.utils.helpers import utc_now


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
        book_repository: BookRepository,
    ) -> None:
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository
        self.book_repository = book_repository

    async def create_order(self, user_id: str, payload: OrderCreateRequest) -> OrderResponse:
        requested_quantities = Counter()
        for item in payload.items:
            requested_quantities[item.book_id] += item.quantity

        book_snapshots: dict[str, tuple[float, int]] = {}
        total_amount = 0.0

        for book_id, quantity in requested_quantities.items():
            book = await self.book_repository.get_by_id(book_id)
            if book is None:
                raise NotFoundException(f"Book {book_id} was not found.")
            if book.stock < quantity:
                raise BadRequestException(f"Insufficient stock for {book.title}.")
            book_snapshots[book_id] = (book.price, quantity)
            total_amount += book.price * quantity

        adjusted_book_ids: list[str] = []
        order: OrderModel | None = None

        try:
            for book_id, (_, quantity) in book_snapshots.items():
                updated_book = await self.book_repository.adjust_stock(book_id, -quantity)
                if updated_book is None:
                    raise BadRequestException("Unable to reserve stock for the selected books.")
                adjusted_book_ids.append(book_id)

            order = await self.order_repository.create_order(
                {
                    "user_id": user_id,
                    "total_amount": round(total_amount, 2),
                    "status": ORDER_STATUS_PENDING,
                    "created_at": utc_now(),
                }
            )

            order_items = await self.order_item_repository.create_many(
                [
                    {
                        "order_id": order.id,
                        "book_id": item.book_id,
                        "quantity": item.quantity,
                        "price": book_snapshots[item.book_id][0],
                        "created_at": utc_now(),
                    }
                    for item in payload.items
                ]
            )
        except Exception:
            for book_id in adjusted_book_ids:
                quantity = book_snapshots[book_id][1]
                await self.book_repository.adjust_stock(book_id, quantity)

            if order is not None:
                await self.order_item_repository.delete_many_by_order_id(order.id)
                await self.order_repository.delete_order(order.id)
            raise

        return self._build_order_response(order, order_items)

    async def list_user_orders(self, user_id: str) -> list[OrderResponse]:
        orders = await self.order_repository.list_by_user_id(user_id)
        return await self._attach_items(orders)

    async def get_user_order(self, user_id: str, order_id: str) -> OrderResponse:
        order = await self.order_repository.get_by_id(order_id)
        if order is None:
            raise NotFoundException("Order not found.")
        if order.user_id != user_id:
            raise ForbiddenException("You can only access your own orders.")
        return await self._attach_single_order(order)

    async def list_all_orders(self) -> list[OrderResponse]:
        orders = await self.order_repository.list_orders()
        return await self._attach_items(orders)

    async def get_sales_report(self) -> SalesReportResponse:
        orders = await self.order_repository.list_orders()
        order_ids = [order.id for order in orders if order.status == ORDER_STATUS_COMPLETED]
        order_items_map = await self.order_item_repository.list_by_order_ids(order_ids)

        gross_revenue = round(
            sum(order.total_amount for order in orders if order.status != ORDER_STATUS_CANCELLED),
            2,
        )
        completed_revenue = round(
            sum(order.total_amount for order in orders if order.status == ORDER_STATUS_COMPLETED),
            2,
        )
        total_items_sold = sum(
            item.quantity
            for order_items in order_items_map.values()
            for item in order_items
        )

        return SalesReportResponse(
            total_orders=len(orders),
            pending_orders=sum(1 for order in orders if order.status == ORDER_STATUS_PENDING),
            completed_orders=sum(1 for order in orders if order.status == ORDER_STATUS_COMPLETED),
            cancelled_orders=sum(1 for order in orders if order.status == ORDER_STATUS_CANCELLED),
            gross_revenue=gross_revenue,
            completed_revenue=completed_revenue,
            total_items_sold=total_items_sold,
            generated_at=utc_now(),
        )

    async def update_order_status(self, order_id: str, status: str) -> OrderResponse:
        if status not in {ORDER_STATUS_PENDING, ORDER_STATUS_COMPLETED, ORDER_STATUS_CANCELLED}:
            raise BadRequestException("Unsupported order status.")

        order = await self.order_repository.update_status(order_id, status)
        if order is None:
            raise NotFoundException("Order not found.")
        return await self._attach_single_order(order)

    async def _attach_items(self, orders: list[OrderModel]) -> list[OrderResponse]:
        order_items_map = await self.order_item_repository.list_by_order_ids([order.id for order in orders])
        return [
            self._build_order_response(order, order_items_map.get(order.id, []))
            for order in orders
        ]

    async def _attach_single_order(self, order: OrderModel) -> OrderResponse:
        items = await self.order_item_repository.list_by_order_id(order.id)
        return self._build_order_response(order, items)

    @staticmethod
    def _build_order_response(order: OrderModel, order_items) -> OrderResponse:
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            items=[
                OrderItemResponse(
                    id=item.id,
                    order_id=item.order_id,
                    book_id=item.book_id,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in order_items
            ],
        )


def get_order_service(database=Depends(get_database)) -> OrderService:
    return OrderService(
        order_repository=OrderRepository(database),
        order_item_repository=OrderItemRepository(database),
        book_repository=BookRepository(database),
    )
