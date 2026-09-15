import pytest

from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.services import user_service
from app.services.exceptions import UserNotFoundError


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
