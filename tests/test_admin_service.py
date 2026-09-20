import pytest

from app.models.admin_model import Admin
from app.schemas.admin_schemas import AdminCreate, AdminUpdate
from app.services import admin_service
from app.services.exceptions import (
    AdminAlreadyExistsError,
    AdminNotFoundError,
    AdminSelfDeleteError,
)


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
    db_session.add(
        Admin(login="admin1", password_hash="secure-pass-1", tg_admin_id=5002, username="duplicate")
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


async def test_admin_service_updates_telegram_link_and_active_status(db_session):
    admin = await admin_service.create_admin(
        AdminCreate(login="admin2", password="already-hashed"),
        db_session,
    )
    assert admin.tg_admin_id is None

    updated = await admin_service.update_admin(
        db_session,
        admin.id,
        AdminUpdate(tg_admin_id=6001, username="linked_now", is_active=False),
    )

    assert updated.tg_admin_id == 6001
    assert updated.username == "linked_now"
    assert updated.is_active is False


async def test_admin_service_update_raises_for_missing_admin(db_session):
    with pytest.raises(AdminNotFoundError):
        await admin_service.update_admin(db_session, 999, AdminUpdate(is_active=False))


async def test_admin_service_update_rejects_duplicate_tg_admin_id(db_session):
    await admin_service.create_admin(
        AdminCreate(login="admin3", password="already-hashed", tg_admin_id=6002),
        db_session,
    )
    admin4 = await admin_service.create_admin(
        AdminCreate(login="admin4", password="already-hashed"),
        db_session,
    )

    with pytest.raises(AdminAlreadyExistsError):
        await admin_service.update_admin(
            db_session,
            admin4.id,
            AdminUpdate(tg_admin_id=6002),
        )


async def test_admin_service_deletes_admin(db_session):
    admin = await admin_service.create_admin(
        AdminCreate(login="admin5", password="already-hashed"),
        db_session,
    )
    other_admin = await admin_service.create_admin(
        AdminCreate(login="admin6", password="already-hashed"),
        db_session,
    )

    await admin_service.delete_admin(db_session, admin.id, acting_admin_id=other_admin.id)

    with pytest.raises(AdminNotFoundError):
        await admin_service.get_admin_by_id(db_session, admin.id)


async def test_admin_service_delete_raises_for_missing_admin(db_session):
    with pytest.raises(AdminNotFoundError):
        await admin_service.delete_admin(db_session, 99999, acting_admin_id=1)


async def test_admin_service_blocks_self_delete(db_session):
    admin = await admin_service.create_admin(
        AdminCreate(login="admin7", password="already-hashed"),
        db_session,
    )

    with pytest.raises(AdminSelfDeleteError):
        await admin_service.delete_admin(db_session, admin.id, acting_admin_id=admin.id)
