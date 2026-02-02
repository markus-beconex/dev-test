# tests/test_tickets.py
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_create_ticket_returns_id():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post(
            "/tickets",
            json={
                "title": "Hello",
                "description": "World",
                "customer_email": "max.mustermann@example.com",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
        assert isinstance(data["id"], int)


@pytest.mark.anyio
async def test_correlation_id_is_returned():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health", headers={"X-Correlation-Id": "abc-123"})
        assert r.status_code == 200
        assert r.headers.get("X-Correlation-Id") == "abc-123"
