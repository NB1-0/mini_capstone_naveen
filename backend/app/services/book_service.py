from __future__ import annotations

from fastapi import Depends

from app.core.database import get_database
from app.exceptions.custom_exceptions import NotFoundException
from app.repositories.book_repository import BookRepository
from app.schemas.book_schema import BookCreate, BookResponse, BookUpdate
from app.utils.helpers import utc_now
from app.utils.validators import ensure_non_negative_stock, ensure_positive_price


class BookService:
    def __init__(self, book_repository: BookRepository) -> None:
        self.book_repository = book_repository

    async def list_books(self) -> list[BookResponse]:
        books = await self.book_repository.list_books()
        return [BookResponse.model_validate(book.model_dump()) for book in books]

    async def get_book(self, book_id: str) -> BookResponse:
        book = await self.book_repository.get_by_id(book_id)
        if book is None:
            raise NotFoundException("Book not found.")
        return BookResponse.model_validate(book.model_dump())

    async def create_book(self, payload: BookCreate) -> BookResponse:
        ensure_positive_price(payload.price)
        ensure_non_negative_stock(payload.stock)

        book = await self.book_repository.create_book(
            {
                "title": payload.title.strip(),
                "author": payload.author.strip(),
                "price": payload.price,
                "stock": payload.stock,
                "created_at": utc_now(),
            }
        )
        return BookResponse.model_validate(book.model_dump())

    async def update_book(self, book_id: str, payload: BookUpdate) -> BookResponse:
        updates = payload.model_dump(exclude_none=True)
        if "price" in updates:
            ensure_positive_price(updates["price"])
        if "stock" in updates:
            ensure_non_negative_stock(updates["stock"])
        if "title" in updates:
            updates["title"] = updates["title"].strip()
        if "author" in updates:
            updates["author"] = updates["author"].strip()

        book = await self.book_repository.update_book(book_id, updates)
        if book is None:
            raise NotFoundException("Book not found.")
        return BookResponse.model_validate(book.model_dump())

    async def delete_book(self, book_id: str) -> None:
        deleted = await self.book_repository.delete_book(book_id)
        if not deleted:
            raise NotFoundException("Book not found.")


def get_book_service(database=Depends(get_database)) -> BookService:
    return BookService(BookRepository(database))
