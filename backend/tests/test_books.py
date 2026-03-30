from __future__ import annotations

import pytest

from app.core.dependencies import require_admin
from app.schemas.book_schema import BookResponse
from app.services.book_service import get_book_service
from tests.conftest import app, build_user

pytestmark = pytest.mark.asyncio


class FakeBookService:
    async def list_books(self):
        return [self._book()]

    async def get_book(self, _book_id):
        return self._book()

    async def create_book(self, _payload):
        return self._book()

    async def update_book(self, _book_id, _payload):
        return self._book()

    async def delete_book(self, _book_id):
        return None

    @staticmethod
    def _book():
        return BookResponse(
            id="book-1",
            title="Clean Code",
            author="Robert C. Martin",
            price=500,
            stock=10,
            created_at=build_user("tmp", "tmp@example.com", "admin").created_at,
        )


async def test_list_books(client):
    app.dependency_overrides[get_book_service] = lambda: FakeBookService()

    response = await client.get("/api/v1/books")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Clean Code"


async def test_create_book_as_admin(client):
    app.dependency_overrides[get_book_service] = lambda: FakeBookService()
    app.dependency_overrides[require_admin] = lambda: build_user("admin-1", "admin@example.com", "admin")

    response = await client.post(
        "/api/v1/books",
        json={"title": "Clean Code", "author": "Robert C. Martin", "price": 500, "stock": 10},
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 201
    assert response.json()["stock"] == 10
