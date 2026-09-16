from datetime import datetime, timedelta, timezone

from app.models.refresh_token_model import RefreshToken
from app.security import generate_refresh_token, hash_refresh_token
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

async def test_refresh_success(client):
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
    test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"}
    )
    old_cookie = test_client.cookies.get("refresh_token")
    response = test_client.post(
    "/auth/refresh/",
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert test_client.cookies.get("refresh_token") != old_cookie


async def test_refresh_reused_token_is_rejected(client):
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
    test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"}
    )
    old_cookie = test_client.cookies.get("refresh_token")
    test_client.post(
        "/auth/refresh/",
    )
    test_client.cookies.set("refresh_token", old_cookie)
    response = test_client.post(
        "/auth/refresh/"
    )
    assert response.status_code == 401

async def test_refresh_expired_token_is_rejected(client):
    test_client, session_factory = client
    async with session_factory() as session:
        admin = await admin_service.create_admin(
            AdminCreate(login="admin",
                        password="password123",
                        tg_admin_id=None,
                        username=None,
            ),
            session,
        )
        raw_token = generate_refresh_token()
        session.add(RefreshToken(
            admin_id=admin.id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        ))
        await session.commit()
    test_client.cookies.set("refresh_token", raw_token)
    response = test_client.post("/auth/refresh/")
    assert response.status_code == 401

async def test_logout_revokes_token(client):
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
    test_client.post(
        "/auth/login/",
        json={"login": "admin", "password": "password123"}
    )
    response_logout = test_client.post(
        "/auth/logout/"
    )
    response_refresh = test_client.post(
        "/auth/refresh/"
    )
    assert response_logout.status_code == 200
    assert response_refresh.status_code == 401