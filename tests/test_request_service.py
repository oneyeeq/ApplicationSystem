from datetime import datetime, timedelta

from sqlalchemy import select

from app.models.request_model import Request, StatusEnum
from app.models.user_model import User
from app.schemas.request_schemas import RequestCreate, RequestUpdate
from app.services.request_service import (
    create_request,
    delete_expired_closed_requests,
    update_request,
)


async def test_cleanup_deletes_old_completed_and_rejected_requests(db_session):
    user = User(tg_user_id=1001, username="tester")
    db_session.add(user)
    await db_session.flush()

    old_date = datetime.now() - timedelta(days=31)
    requests = [
        Request(
            service_name="Сайт",
            phone_number="+10000000000",
            user_id=user.id,
            status=StatusEnum.COMPLETED,
            created_at=old_date,
            updated_at=old_date,
        ),
        Request(
            service_name="Бот",
            phone_number="+10000000001",
            user_id=user.id,
            status=StatusEnum.REJECTED,
            created_at=old_date,
            updated_at=old_date,
        ),
        Request(
            service_name="Скрипт",
            phone_number="+10000000002",
            user_id=user.id,
            status=StatusEnum.NEW,
            created_at=old_date,
            updated_at=old_date,
        ),
    ]
    db_session.add_all(requests)
    await db_session.commit()

    deleted_count = await delete_expired_closed_requests(db_session, datetime.now())

    remaining = (
        await db_session.execute(select(Request).order_by(Request.id))
    ).scalars().all()

    assert deleted_count == 2
    assert len(remaining) == 1
    assert remaining[0].status is StatusEnum.NEW


async def test_cleanup_keeps_recent_closed_request(db_session):
    user = User(tg_user_id=1002)
    db_session.add(user)
    await db_session.flush()

    recent_date = datetime.now() - timedelta(days=1)
    db_session.add(
        Request(
            service_name="Сайт",
            phone_number="+10000000003",
            user_id=user.id,
            status=StatusEnum.COMPLETED,
            created_at=recent_date,
            updated_at=recent_date,
        )
    )
    await db_session.commit()

    cutoff = datetime.now() - timedelta(days=30)
    deleted_count = await delete_expired_closed_requests(db_session, cutoff)

    assert deleted_count == 0


async def test_request_lifecycle_updates_user_active_count(db_session):
    user = User(tg_user_id=1003)
    db_session.add(user)
    await db_session.commit()

    request = await create_request(
        db_session,
        telegram_id=user.tg_user_id,
        request_data=RequestCreate(
            service_name="Сайт",
            phone_number="+10000000004",
        ),
    )

    assert request.status is StatusEnum.NEW
    assert user.active_requests == 1

    await update_request(
        db_session,
        request.id,
        RequestUpdate(status=StatusEnum.IN_PROGRESS),
    )
    await update_request(
        db_session,
        request.id,
        RequestUpdate(status=StatusEnum.COMPLETED),
    )

    assert user.active_requests == 0
