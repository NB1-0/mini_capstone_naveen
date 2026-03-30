from __future__ import annotations

import pytest

from app.core.dependencies import require_admin, require_customer
from app.schemas.order_item_schema import OrderItemResponse
from app.schemas.order_schema import OrderResponse, SalesReportResponse
from app.services.order_service import get_order_service
from tests.conftest import app, build_user

pytestmark = pytest.mark.asyncio


class FakeOrderService:
    async def create_order(self, user_id, _payload):
        return self._order(user_id)

    async def list_user_orders(self, user_id):
        return [self._order(user_id)]

    async def get_user_order(self, user_id, _order_id):
        return self._order(user_id)

    async def list_all_orders(self):
        return [self._order("customer-1")]

    async def get_sales_report(self):
        return SalesReportResponse(
            total_orders=1,
            pending_orders=1,
            completed_orders=0,
            cancelled_orders=0,
            gross_revenue=1000,
            completed_revenue=0,
            total_items_sold=0,
            generated_at=build_user("tmp", "tmp@example.com", "admin").created_at,
        )

    async def update_order_status(self, _order_id, _status):
        return self._order("customer-1")

    @staticmethod
    def _order(user_id: str):
        return OrderResponse(
            id="order-1",
            user_id=user_id,
            total_amount=1000,
            status="pending",
            created_at=build_user("tmp", "tmp@example.com", "admin").created_at,
            items=[
                OrderItemResponse(
                    id="item-1",
                    order_id="order-1",
                    book_id="book-1",
                    quantity=2,
                    price=500,
                )
            ],
        )


async def test_create_order(client):
    app.dependency_overrides[get_order_service] = lambda: FakeOrderService()
    app.dependency_overrides[require_customer] = lambda: build_user("customer-1", "customer@example.com", "customer")

    response = await client.post(
        "/api/v1/orders",
        json={"items": [{"book_id": "book-1", "quantity": 2}]},
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 201
    assert response.json()["total_amount"] == 1000


async def test_customer_orders(client):
    app.dependency_overrides[get_order_service] = lambda: FakeOrderService()
    app.dependency_overrides[require_customer] = lambda: build_user("customer-1", "customer@example.com", "customer")

    response = await client.get("/api/v1/orders", headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json()[0]["items"][0]["quantity"] == 2


async def test_admin_sales_report(client):
    app.dependency_overrides[get_order_service] = lambda: FakeOrderService()
    app.dependency_overrides[require_admin] = lambda: build_user("admin-1", "admin@example.com", "admin")

    response = await client.get("/api/v1/admin/salesreport", headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json()["gross_revenue"] == 1000
