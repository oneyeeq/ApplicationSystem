from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.security import decode_access_token
from app.models.admin_model import Admin
from app.services.exceptions import AdminNotFoundError, AdminIsNotActiveError

bearer_scheme = HTTPBearer()


async def get_admin_from_token(token: str, db: AsyncSession) -> Admin:
    """Общая логика проверки JWT, переиспользуется get_current_admin
    и комбинированной проверкой в service_or_admin_auth.py."""
    try:
        login = decode_access_token(token)
        result = await db.execute(select(Admin).where(Admin.login == login))
        admin = result.scalar_one_or_none()
        if not admin:
            raise AdminNotFoundError("Админ не найден")
        if not admin.is_active:
            raise AdminIsNotActiveError("Админ не активен")
        return admin
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен недействителен или истёк",
        )
    except AdminNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Админ не найден",
        )
    except AdminIsNotActiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт администратора деактивирован",
        )


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    return await get_admin_from_token(credentials.credentials, db)