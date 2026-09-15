from fastapi.testclient import TestClient
import httpx

from app.main import app

client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")

async def test_health_returns_ok():
    response = await client.get()
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

        