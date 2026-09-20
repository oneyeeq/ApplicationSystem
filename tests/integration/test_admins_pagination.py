from app.schemas.admin_schemas import AdminCreate
from app.services import admin_service


async def _create_admin_and_login(test_client, session_factory, login: str) -> str:
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login=login, password="password123", tg_admin_id=None, username=None),
            session,
        )
    login_response = test_client.post(
        "/auth/login/",
        json={"login": login, "password": "password123"},
    )
    return login_response.json()["access_token"]


async def test_paginated_admins_returns_envelope_with_correct_page(client):
    test_client, session_factory = client
    token = await _create_admin_and_login(test_client, session_factory, "admin1")
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin2", password="password123", tg_admin_id=None, username=None),
            session,
        )
        await admin_service.create_admin(
            AdminCreate(login="admin3", password="password123", tg_admin_id=None, username=None),
            session,
        )

    response = test_client.get(
        "/admins/paginated",
        params={"page": 1, "page_size": 2},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2


async def test_paginated_admins_requires_authorization(client):
    test_client, session_factory = client
    response = test_client.get("/admins/paginated")

    assert response.status_code == 401
