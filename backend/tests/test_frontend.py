from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_root_serves_frontend(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert "StoryShelf Console" in response.text
    assert "/assets/app.js" in response.text
