from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.controllers import book_controller
from app.core.dependencies import require_admin
from app.models.user_model import UserModel
from app.schemas.book_schema import BookCreate, BookResponse, BookUpdate
from app.services.book_service import BookService, get_book_service

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookResponse])
async def list_books(service: BookService = Depends(get_book_service)) -> list[BookResponse]:
    return await book_controller.list_books(service)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, service: BookService = Depends(get_book_service)) -> BookResponse:
    return await book_controller.get_book(book_id, service)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    _: UserModel = Depends(require_admin),
    service: BookService = Depends(get_book_service),
) -> BookResponse:
    return await book_controller.create_book(payload, service)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    payload: BookUpdate,
    _: UserModel = Depends(require_admin),
    service: BookService = Depends(get_book_service),
) -> BookResponse:
    return await book_controller.update_book(book_id, payload, service)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    _: UserModel = Depends(require_admin),
    service: BookService = Depends(get_book_service),
) -> Response:
    await book_controller.delete_book(book_id, service)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
