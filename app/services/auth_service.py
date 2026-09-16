from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth_schemas import LoginRequest, LoginResponse
from app.models.admin_model import Admin
from app.services.exceptions import AdminNotFoundError, AdminIsNotActiveError, PasswordNotValidError
from datetime import datetime, timedelta, timezone
from config import settings
from app.models.refresh_token_model import RefreshToken
from app.security import verify_password, create_access_token, generate_refresh_token, hash_refresh_token


async def authenticate_admin(
    request_data: LoginRequest,
    db: AsyncSession,
) -> tuple[LoginResponse, str]:
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
    raw_refresh_token = generate_refresh_token()
    expired_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(admin_id=admin.id, token_hash=hash_refresh_token(raw_refresh_token), expires_at=expired_at)
    db.add(refresh_token)
    await db.commit()
    return LoginResponse(access_token=token, token_type="bearer"), raw_refresh_token
