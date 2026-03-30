from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.mongo_client import create_mongo_client
from app.utils.constants import ROLE_ADMIN, USERS_COLLECTION
from app.utils.helpers import utc_now


async def main() -> None:
    settings = get_settings()
    client = create_mongo_client(settings.mongodb_url)
    database = client[settings.mongodb_db_name]
    collection = database[USERS_COLLECTION]

    existing = await collection.find_one({"email": settings.admin_email.lower()})
    if existing:
        client.close()
        print("Admin user already exists.")
        return

    await collection.insert_one(
        {
            "email": settings.admin_email.lower(),
            "password": hash_password(settings.admin_password),
            "role": ROLE_ADMIN,
            "created_at": utc_now(),
        }
    )
    client.close()
    print(f"Created admin user: {settings.admin_email}")


if __name__ == "__main__":
    asyncio.run(main())
