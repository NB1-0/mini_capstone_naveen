from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_root_serves_frontend(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert "StoryShelf Console" in response.text
    assert "/assets/app.js" in response.text
    assert "/assets/simple.css" in response.text


async def test_frontend_assets_are_available(client):
    css_response = await client.get("/assets/simple.css")
    assert css_response.status_code == 200
    assert ".book-card" in css_response.text

    js_response = await client.get("/assets/app.js")
    assert js_response.status_code == 200
    assert "const API_PREFIX" in js_response.text
