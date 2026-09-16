from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.services.exceptions import UserNotFoundError
from app.services.request_service import has_reached_active_limit


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User:
    result = await db.execute(select(User).where(User.tg_user_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError
    return user


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    user = User(**user_data.model_dump())
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
    user = await get_user_by_id(db, user_id)
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user

async def can_create_request(db: AsyncSession, telegram_id: int) -> dict:
    result = await db.execute(select(User).where(User.tg_user_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError

    if not user.is_active:
        return {"allowed": False, "error": "inactive"}

    if has_reached_active_limit(user):
        return {"allowed": False, "error": "limit"}

    return {"allowed": True, "error": None}