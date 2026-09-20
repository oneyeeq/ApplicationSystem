import pytest

from app.models.request_model import Request, StatusEnum
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.services import user_service
from app.services.exceptions import UserHasRequestsError, UserNotFoundError


async def test_user_can_be_created_found_and_updated(db_session):
    user = await user_service.create_user(
        db_session,
        UserCreate(tg_user_id=2001, username="first"),
    )

    assert user.tg_user_id == 2001
    assert user.active_requests == 0

    found = await user_service.get_user_by_telegram_id(db_session, 2001)
    assert found.id == user.id

    updated = await user_service.update_user(
        db_session,
        user.id,
        UserUpdate(is_active=False),
    )
    assert updated.is_active is False


async def test_missing_user_raises_domain_error(db_session):
    with pytest.raises(UserNotFoundError):
        await user_service.get_user_by_id(db_session, 99999)


async def test_inactive_user_cannot_create_request(db_session):
    db_session.add(User(tg_user_id=2002, is_active=False))
    await db_session.commit()

    result = await user_service.can_create_request(db_session, 2002)

    assert result == {"allowed": False, "error": "inactive"}


async def test_delete_user_removes_user_without_requests(db_session):
    user = await user_service.create_user(
        db_session,
        UserCreate(tg_user_id=2003, username="to_delete"),
    )

    await user_service.delete_user(db_session, user.id)

    with pytest.raises(UserNotFoundError):
        await user_service.get_user_by_id(db_session, user.id)


async def test_delete_user_raises_for_missing_user(db_session):
    with pytest.raises(UserNotFoundError):
        await user_service.delete_user(db_session, 99999)


async def test_delete_user_blocked_when_user_has_requests(db_session):
    user = User(tg_user_id=2004, username="with_requests")
    db_session.add(user)
    await db_session.flush()
    db_session.add(
        Request(
            service_name="Сайт",
            phone_number="+10000000003",
            user_id=user.id,
            status=StatusEnum.NEW,
        )
    )
    await db_session.commit()

    with pytest.raises(UserHasRequestsError):
        await user_service.delete_user(db_session, user.id)


async def test_list_users_paginated_orders_newest_first_and_reports_total(db_session):
    for i in range(3):
        db_session.add(User(tg_user_id=2100 + i, username=f"user_{i}"))
    await db_session.commit()

    items, total = await user_service.list_users_paginated(db_session, page=1, page_size=2)

    assert total == 3
    assert len(items) == 2
    assert items[0].tg_user_id == 2102
