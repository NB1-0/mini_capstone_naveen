from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.core.config import get_settings
from app.db.mongo_client import create_mongo_client
from app.utils.constants import BOOKS_COLLECTION
from app.utils.helpers import utc_now


SAMPLE_BOOKS = [
    {"title": "Clean Code", "author": "Robert C. Martin", "price": 500, "stock": 10},
    {"title": "The Pragmatic Programmer", "author": "Andy Hunt", "price": 650, "stock": 8},
    {"title": "Refactoring", "author": "Martin Fowler", "price": 700, "stock": 6},
    {"title": "Design Patterns", "author": "Erich Gamma", "price": 900, "stock": 5},
]


async def main() -> None:
    settings = get_settings()
    client = create_mongo_client(settings.mongodb_url)
    database = client[settings.mongodb_db_name]
    collection = database[BOOKS_COLLECTION]

    documents = [{**book, "created_at": utc_now()} for book in SAMPLE_BOOKS]
    await collection.insert_many(documents)
    client.close()
    print(f"Inserted {len(documents)} sample books into {settings.mongodb_db_name}.")


if __name__ == "__main__":
    asyncio.run(main())
