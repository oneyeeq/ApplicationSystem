from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth_schemas import LoginRequest, LoginResponse
from app.models.admin_model import Admin
from app.services.exceptions import AdminNotFoundError, AdminIsNotActiveError, PasswordNotValidError
from app.security import verify_password, create_access_token


async def authenticate_admin(
    request_data: LoginRequest,
    db: AsyncSession,
) -> LoginResponse:
    result = await db.execute(select(Admin).where(Admin.login == request_data.login))
    admin = result.scalar_one_or_none()
    if not admin:
        raise AdminNotFoundError("Админ не найден")
    if not admin.is_active:
        raise AdminIsNotActiveError("Админ не активен")
    success = verify_password(request_data.password, admin.password_hash)
    if not success:
        raise PasswordNotValidError("Пароль неправильный")
    token = create_access_token(admin.login)
    return LoginResponse(access_token=token, token_type="bearer")