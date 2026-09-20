from app.models.admin_model import Admin
from app.models.user_model import User
from app.security import hash_password
from config import settings


async def _login(test_client) -> str:
    login_response = test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"},
    )
    return login_response.json()["access_token"]


async def test_paginated_users_returns_envelope_with_correct_page(client):
    test_client, session_factory = client
    async with session_factory() as session:
        session.add(
            Admin(login="admin", password_hash=hash_password("password123"), tg_admin_id=None)
        )
        session.add_all([User(tg_user_id=5000 + i) for i in range(3)])
        await session.commit()

    token = await _login(test_client)
    response = test_client.get(
        "/users/paginated",
        params={"page": 1, "page_size": 2},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2


async def test_paginated_users_requires_authorization(client):
    test_client, session_factory = client
    response = test_client.get("/users/paginated")

    assert response.status_code == 401


async def test_paginated_users_accepts_service_token(client):
    test_client, session_factory = client
    response = test_client.get(
        "/users/paginated",
        headers={"X-Service-Token": settings.SERVICE_TOKEN},
    )

    assert response.status_code == 200
