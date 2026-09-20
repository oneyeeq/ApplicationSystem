from app.schemas.admin_schemas import AdminCreate
from app.services import admin_service
from config import settings


async def test_get_active_admins_with_valid_service_token(client):
    test_client, session_factory = client
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin", password="password123", tg_admin_id=12345, username=None),
            session,
        )
    response = test_client.get(
        "/admins/active",
        headers={"X-Service-Token": settings.SERVICE_TOKEN},
    )
    assert response.status_code == 200


async def test_get_active_admins_without_service_token(client):
    test_client, session_factory = client
    response = test_client.get("/admins/active")
    assert response.status_code == 401


async def test_get_active_admins_with_wrong_service_token(client):
    test_client, session_factory = client
    response = test_client.get(
        "/admins/active",
        headers={"X-Service-Token": "wrong-token"},
    )
    assert response.status_code == 401


async def test_get_users_with_valid_service_token(client):
    test_client, session_factory = client
    response = test_client.get(
        "/users/",
        headers={"X-Service-Token": settings.SERVICE_TOKEN},
    )
    assert response.status_code == 200


async def test_get_users_without_service_token(client):
    test_client, session_factory = client
    response = test_client.get("/users/")
    assert response.status_code == 401


async def test_get_requests_with_valid_service_token(client):
    test_client, session_factory = client
    response = test_client.get(
        "/requests/",
        headers={"X-Service-Token": settings.SERVICE_TOKEN},
    )
    assert response.status_code == 200


async def test_get_requests_without_service_token(client):
    test_client, session_factory = client
    response = test_client.get("/requests/")
    assert response.status_code == 401


async def test_get_requests_with_admin_jwt(client):
    test_client, session_factory = client
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin", password="password123", tg_admin_id=None, username=None),
            session,
        )
    login_response = test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    response = test_client.get(
        "/requests/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


async def test_get_users_with_admin_jwt(client):
    test_client, session_factory = client
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin", password="password123", tg_admin_id=None, username=None),
            session,
        )
    login_response = test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    response = test_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


async def test_get_requests_with_invalid_jwt_and_no_service_token(client):
    test_client, session_factory = client
    response = test_client.get(
        "/requests/",
        headers={"Authorization": "Bearer garbage-token"},
    )
    assert response.status_code == 401
