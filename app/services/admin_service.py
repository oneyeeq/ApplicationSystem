from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_model import Admin
from app.schemas.admin_schemas import AdminCreate, AdminUpdate
from app.security import hash_password
from app.services.exceptions import (
    AdminAlreadyExistsError,
    AdminNotFoundError,
    AdminSelfDeleteError,
)


async def get_active_admins(db: AsyncSession) -> list[Admin]:
    result = await db.execute(
        select(Admin).where(Admin.is_active.is_(True), Admin.tg_admin_id.is_not(None))
    )
    admins = list(result.scalars().all())
    if not admins:
        raise AdminNotFoundError("Активные админы не найдены")
    return admins


async def create_admin(admin_data: AdminCreate, db: AsyncSession) -> Admin:
    admin = Admin(
        login=admin_data.login,
        password_hash=hash_password(admin_data.password),
        tg_admin_id=admin_data.tg_admin_id,
        username=admin_data.username,
    )
    db.add(admin)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AdminAlreadyExistsError("Админ уже существует")
    await db.refresh(admin)
    return admin


async def delete_admin(db: AsyncSession, admin_id: int, acting_admin_id: int) -> None:
    if admin_id == acting_admin_id:
        raise AdminSelfDeleteError("Нельзя удалить самого себя")
    admin = await get_admin_by_id(db, admin_id)
    await db.delete(admin)
    await db.commit()


async def get_admins(db: AsyncSession) -> list[Admin]:
    result = await db.execute(select(Admin))
    admins = list(result.scalars().all())
    return admins


async def get_admin_by_id(db: AsyncSession, admin_id: int) -> Admin:
    admin = await db.get(Admin, admin_id)
    if admin is None:
        raise AdminNotFoundError("Админ не найден")
    return admin


async def update_admin(db: AsyncSession, admin_id: int, admin_data: AdminUpdate) -> Admin:
    admin = await get_admin_by_id(db, admin_id)
    for field, value in admin_data.model_dump(exclude_unset=True).items():
        setattr(admin, field, value)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AdminAlreadyExistsError("Админ с таким tg_admin_id уже существует")
    await db.refresh(admin)
    return admin
