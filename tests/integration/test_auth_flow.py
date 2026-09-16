from app.schemas.admin_schemas import AdminCreate
from app.services import admin_service
from app.models.admin_model import Admin
from app.security import hash_password

async def test_login_success(client):
    test_client, session_factory = client
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin",
                        password="password123",
                        tg_admin_id=None,
                        username=None
            ),
            session,
        )
    response = test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

async def test_login_wrong_password(client):
    test_client, session_factory = client
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin",
                        password="password123",
                        tg_admin_id=None,
                        username=None
            ),
            session,
        )
    response = test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password124"}
    )
    assert response.status_code == 401

async def test_login_unknown_login(client):
    test_client, session_factory = client
    response = test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"}
    )
    assert response.status_code == 401

async def test_login_inactive_admin(client):
    test_client, session_factory = client
    async with session_factory() as session:
        session.add(Admin(
            login="admin",
            password_hash=hash_password("password123"),
            tg_admin_id=5002,
            username="duplicate",
            is_active=False,
        ))
        await session.commit()
    response = test_client.post(
            "/auth/login/",
            json={"login": "admin", "password": "password123"},
        )
    assert response.status_code == 401

async def test_create_admin_with_valid_token(client):
    test_client, session_factory = client
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin",
                        password="password123",
                        tg_admin_id=None,
                        username=None
            ),
            session,
        )
    response = test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"}
    )
    token = response.json()["access_token"]
    response = test_client.post(
        "/admins/",
        json={"login": "admin1", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

async def test_create_admin_without_token(client):
    test_client, session_factory = client
    response = test_client.post(
        "/admins/",
        json={},
        headers={},
    )
    assert response.status_code == 401

async def test_create_admin_with_tampered_token(client):
    test_client, session_factory = client
    async with session_factory() as session:
        await admin_service.create_admin(
            AdminCreate(login="admin",
                        password="password123",
                        tg_admin_id=None,
                        username=None
            ),
            session,
        )
    response = test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"}
    )
    token = response.json()["access_token"] + "modified"
    response = test_client.post(
        "/admins/",
        json={"login": "admin1", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401