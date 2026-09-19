from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_model import Admin
from app.schemas.admin_schemas import AdminCreate
from app.security import hash_password
from app.services.exceptions import AdminAlreadyExistsError, AdminNotFoundError

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

async def get_admins(db: AsyncSession) -> list[Admin]:
    result = await db.execute(select(Admin))
    admins = list(result.scalars().all())
    return admins