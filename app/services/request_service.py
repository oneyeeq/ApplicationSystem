from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request_archive_model import ArchivedRequest
from app.models.request_model import Request, StatusEnum
from app.models.user_model import User
from app.schemas.request_schemas import RequestCreate, RequestUpdate
from app.services.exceptions import (
    ActiveRequestLimitError,
    InactiveUserError,
    RequestAlreadyClosedError,
    RequestNotFoundError,
    RequestTransitionNotAllowedError,
)
from app.services.user_service import get_user_by_id, get_user_by_telegram_id
from config import settings

ACTIVE_STATUSES = {
    StatusEnum.NEW,
    StatusEnum.IN_PROGRESS,
}
CLOSED_STATUSES = {
    StatusEnum.COMPLETED,
    StatusEnum.REJECTED,
}
ALLOWED_TRANSITIONS = {
    (StatusEnum.NEW, StatusEnum.IN_PROGRESS),
    (StatusEnum.NEW, StatusEnum.REJECTED),
    (StatusEnum.IN_PROGRESS, StatusEnum.COMPLETED),
    (StatusEnum.IN_PROGRESS, StatusEnum.REJECTED),
}


async def create_request(
    db: AsyncSession,
    telegram_id: int,
    request_data: RequestCreate,
) -> Request:
    user = await get_user_by_telegram_id(db, telegram_id)
    _validate_user_active(user)

    reserved = await db.execute(
        update(User)
        .where(User.id == user.id, User.active_requests < settings.MAX_ACTIVE_REQUESTS)
        .values(active_requests=User.active_requests + 1)
    )
    if reserved.rowcount == 0:
        raise ActiveRequestLimitError("Достигнут лимит активных заявок")

    request = Request(**request_data.model_dump(), user_id=user.id)
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def list_requests(db: AsyncSession) -> list[Request]:
    result = await db.execute(select(Request).order_by(Request.created_at.asc(), Request.id.asc()))
    return list(result.scalars().all())


async def list_user_requests(
    db: AsyncSession,
    telegram_id: int,
) -> list[Request]:
    user = await get_user_by_telegram_id(db, telegram_id)
    result = await db.execute(
        select(Request)
        .where(Request.user_id == user.id)
        .order_by(Request.created_at.desc(), Request.id.desc())
    )
    return list(result.scalars().all())


async def get_request(db: AsyncSession, request_id: int) -> Request:
    result = await db.execute(select(Request).where(Request.id == request_id))
    request = result.scalar_one_or_none()
    if request is None:
        raise RequestNotFoundError("Заявка не найдена")
    return request


async def update_request(
    db: AsyncSession,
    request_id: int,
    request_data: RequestUpdate,
) -> Request:
    request = await get_request(db, request_id)
    old_status = request.status
    if old_status in CLOSED_STATUSES:
        raise RequestAlreadyClosedError("Заявка уже закрыта или отклонена")
    if (old_status, request_data.status) not in ALLOWED_TRANSITIONS:
        raise RequestTransitionNotAllowedError("Заявка не может быть изменена")
    request.status = request_data.status
    if _is_status_transition(old_status, request.status, ACTIVE_STATUSES, CLOSED_STATUSES):
        user = await get_user_by_id(db, request.user_id)
        _adjust_active_requests(user, delta=-1)

    await db.commit()
    await db.refresh(request)
    return request


async def delete_request(db: AsyncSession, request_id: int) -> None:
    request = await get_request(db, request_id)
    if request.status in ACTIVE_STATUSES:
        user = await get_user_by_id(db, request.user_id)
        _adjust_active_requests(user, delta=-1)
    await db.delete(request)
    await db.commit()


async def archive_stale_requests(
    db: AsyncSession,
    older_than: datetime,
) -> int:
    results = await db.execute(
        select(Request).where(
            Request.updated_at < older_than,
        )
    )
    requests = list(results.scalars().all())
    for request in requests:
        archived_request = ArchivedRequest(
            original_request_id=request.id,
            service_name=request.service_name,
            phone_number=request.phone_number,
            status=request.status,
            created_at=request.created_at,
            updated_at=request.updated_at,
        )
        db.add(archived_request)
        await db.delete(request)
    await db.commit()
    return len(requests)


# -- Helpers --


def _validate_user_active(user: User) -> None:
    if not user.is_active:
        raise InactiveUserError("Пользователь заблокирован")


def _is_status_transition(
    old: StatusEnum,
    new: StatusEnum,
    from_set: set[StatusEnum],
    to_set: set[StatusEnum],
) -> bool:
    return old in from_set and new in to_set


def _adjust_active_requests(user: User, delta: int) -> None:
    if user.active_requests + delta < 0:
        return
    user.active_requests += delta
