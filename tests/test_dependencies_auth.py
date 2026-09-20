import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies.auth import get_current_admin
from app.models.admin_model import Admin
from app.schemas.admin_schemas import AdminCreate
from app.security import (
    create_access_token,
)
from app.services import admin_service


async def test_get_current_admin_returns_admin_for_valid_token(db_session):
    admin = await admin_service.create_admin(
        AdminCreate(
            login="admin1",
            password="already-hashed",
            tg_admin_id=5001,
            username="duplicate",
        ),
        db_session,
    )
    token = create_access_token(admin.login)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    result = await get_current_admin(credentials=credentials, db=db_session)
    assert result == admin


async def test_get_current_admin_rejects_tampered_token(db_session):
    token = create_access_token("admin") + "modified"
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(credentials=credentials, db=db_session)
    assert exc_info.value.status_code == 401


async def test_get_current_admin_rejects_unknown_login(db_session):
    token = create_access_token("unknown-login")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(credentials=credentials, db=db_session)
    assert exc_info.value.status_code == 401


async def test_get_current_admin_rejects_inactive_admin(db_session):
    db_session.add(
        Admin(
            login="admin1",
            password_hash="secure-pass-1",
            tg_admin_id=5002,
            username="duplicate",
            is_active=False,
        )
    )
    await db_session.commit()
    token = create_access_token("admin1")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(credentials=credentials, db=db_session)
    assert exc_info.value.status_code == 403
