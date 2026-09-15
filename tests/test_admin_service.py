import pytest

from app.models.admin_model import Admin
from app.schemas.admin_schemas import AdminCreate
from app.services import admin_service
from app.services.exceptions import AdminAlreadyExistsError, AdminNotFoundError


async def test_admin_service_creates_and_lists_active_admin(db_session):
    admin = await admin_service.create_admin(
        AdminCreate(
            login="admin1",
            password="already-hashed",
            tg_admin_id=5001,
            username="duplicate",
        ),
        db_session,
    )

    assert admin.tg_admin_id == 5001
    assert (await admin_service.get_active_admins(db_session)) == [admin]


async def test_admin_service_rejects_duplicate_admin(db_session):
    db_session.add(Admin(
        login="admin1",
        password_hash="secure-pass-1",
        tg_admin_id=5002,
        username="duplicate"
        )
    )
    await db_session.commit()

    with pytest.raises(AdminAlreadyExistsError):
        await admin_service.create_admin(
            AdminCreate(
                login="admin1",
                password="secure-pass-1",
                tg_admin_id=5002,
                username="duplicate",
            ),
            db_session,
        )


async def test_admin_service_reports_no_active_admins(db_session):
    with pytest.raises(AdminNotFoundError):
        await admin_service.get_active_admins(db_session)
