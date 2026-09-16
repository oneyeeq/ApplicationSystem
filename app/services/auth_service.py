from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from app.schemas.auth_schemas import LoginRequest, LoginResponse
from app.models.admin_model import Admin
from app.models.refresh_token_model import RefreshToken
from app.services.exceptions import (
    AdminNotFoundError,
    AdminIsNotActiveError,
    PasswordNotValidError,
    RefreshTokenExpiredError,
    RefreshTokenInvalidError,
)
from config import settings
from app.security import (
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)


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

async def refresh_access_token(
    raw_refresh_token: str,
    db: AsyncSession,
) -> tuple[str, str]:
    token_hash = hash_refresh_token(raw_refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored_token = result.scalar_one_or_none()
    if not stored_token:
        raise RefreshTokenInvalidError("Токен не найден")
    expires_at = stored_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise RefreshTokenExpiredError("Токен истёк")
    if stored_token.revoked_at is not None:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.admin_id == stored_token.admin_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await db.commit()
        raise RefreshTokenInvalidError("Токен не найден")
    stored_token.revoked_at = datetime.now(timezone.utc)
    admin = await db.get(Admin, stored_token.admin_id)
    if not admin.is_active: 
        raise AdminIsNotActiveError("Админ не активен")
    new_access_token = create_access_token(admin.login)
    new_raw_refresh_token = generate_refresh_token()
    expired_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(admin_id=admin.id, token_hash=hash_refresh_token(new_raw_refresh_token), expires_at=expired_at)
    db.add(refresh_token)
    await db.commit()
    return new_access_token, new_raw_refresh_token