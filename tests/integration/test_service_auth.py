from config import settings
from app.schemas.admin_schemas import AdminCreate
from app.services import admin_service


async def test_get_active_admins_with_valid_service_token(client):
    test_client, session_factory = client
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin", password="password123", tg_admin_id=None, username=None),
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
