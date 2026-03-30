from __future__ import annotations

from app.exceptions.custom_exceptions import BadRequestException


def ensure_non_negative_stock(stock: int) -> None:
    if stock < 0:
        raise BadRequestException("Stock cannot be negative.")


def ensure_positive_price(price: float) -> None:
    if price <= 0:
        raise BadRequestException("Price must be greater than zero.")
