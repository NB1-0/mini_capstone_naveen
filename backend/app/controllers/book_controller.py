from __future__ import annotations

from app.schemas.book_schema import BookCreate, BookResponse, BookUpdate
from app.services.book_service import BookService


async def list_books(service: BookService) -> list[BookResponse]:
    return await service.list_books()


async def get_book(book_id: str, service: BookService) -> BookResponse:
    return await service.get_book(book_id)


async def create_book(payload: BookCreate, service: BookService) -> BookResponse:
    return await service.create_book(payload)


async def update_book(book_id: str, payload: BookUpdate, service: BookService) -> BookResponse:
    return await service.update_book(book_id, payload)


async def delete_book(book_id: str, service: BookService) -> None:
    await service.delete_book(book_id)
