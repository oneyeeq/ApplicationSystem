from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from app.models.request_archive_model import ArchivedRequest
from app.models.request_model import Request, StatusEnum
from app.models.user_model import User
from app.schemas.request_schemas import RequestCreate, RequestUpdate
from app.services.exceptions import ActiveRequestLimitError
from app.services.request_service import (
    archive_stale_requests,
    create_request,
    list_requests_paginated,
    update_request,
)
from config import settings


async def test_archive_moves_all_stale_requests_regardless_of_status(db_session):
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
    original_ids = [r.id for r in requests]

    archived_count = await archive_stale_requests(db_session, datetime.now())

    remaining = (await db_session.execute(select(Request).order_by(Request.id))).scalars().all()
    archived = (
        (await db_session.execute(select(ArchivedRequest).order_by(ArchivedRequest.id)))
        .scalars()
        .all()
    )

    assert archived_count == 3
    assert remaining == []
    assert [a.original_request_id for a in archived] == original_ids
    assert {a.status for a in archived} == {
        StatusEnum.COMPLETED,
        StatusEnum.REJECTED,
        StatusEnum.NEW,
    }


async def test_archive_keeps_recent_request(db_session):
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
    archived_count = await archive_stale_requests(db_session, cutoff)

    assert archived_count == 0


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


async def test_create_request_rejects_when_limit_reached(db_session):
    user = User(tg_user_id=1004, active_requests=settings.MAX_ACTIVE_REQUESTS)
    db_session.add(user)
    await db_session.commit()

    with pytest.raises(ActiveRequestLimitError):
        await create_request(
            db_session,
            telegram_id=user.tg_user_id,
            request_data=RequestCreate(
                service_name="Сайт",
                phone_number="+10000000005",
            ),
        )

    # the guarded UPDATE must not have created an orphan Request row
    # when it correctly matched 0 rows
    result = await db_session.execute(select(Request).where(Request.user_id == user.id))
    assert result.scalars().all() == []


async def test_list_requests_paginated_orders_newest_first_and_reports_total(db_session):
    user = User(tg_user_id=1005)
    db_session.add(user)
    await db_session.flush()

    base_time = datetime.now()
    requests = [
        Request(
            service_name=f"Услуга {i}",
            phone_number=f"+2000000000{i}",
            user_id=user.id,
            status=StatusEnum.NEW,
            created_at=base_time + timedelta(minutes=i),
            updated_at=base_time + timedelta(minutes=i),
        )
        for i in range(5)
    ]
    db_session.add_all(requests)
    await db_session.commit()

    items, total = await list_requests_paginated(db_session, page=1, page_size=2)

    assert total == 5
    assert [r.service_name for r in items] == ["Услуга 4", "Услуга 3"]


async def test_list_requests_paginated_returns_remaining_items_on_last_page(db_session):
    user = User(tg_user_id=1006)
    db_session.add(user)
    await db_session.flush()

    base_time = datetime.now()
    requests = [
        Request(
            service_name=f"Услуга {i}",
            phone_number=f"+3000000000{i}",
            user_id=user.id,
            status=StatusEnum.NEW,
            created_at=base_time + timedelta(minutes=i),
            updated_at=base_time + timedelta(minutes=i),
        )
        for i in range(5)
    ]
    db_session.add_all(requests)
    await db_session.commit()

    items, total = await list_requests_paginated(db_session, page=3, page_size=2)

    assert total == 5
    assert [r.service_name for r in items] == ["Услуга 0"]


async def test_list_requests_paginated_empty_table(db_session):
    items, total = await list_requests_paginated(db_session, page=1, page_size=20)

    assert items == []
    assert total == 0
