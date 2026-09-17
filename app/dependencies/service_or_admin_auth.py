import hmac

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_admin_from_token
from config import settings


async def verify_service_token_or_admin(
    x_service_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Пропускает либо бота (X-Service-Token), либо залогиненного админа
    (Authorization: Bearer <JWT>). Нужна там, где один и тот же ресурс
    (заявки, пользователи) должны видеть и менять и бот, и веб-панель."""
    if x_service_token is not None and hmac.compare_digest(
        x_service_token, settings.SERVICE_TOKEN
    ):
        return

    if authorization is not None and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
        await get_admin_from_token(token, db)
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Требуется сервисный токен или действующая JWT-сессия администратора",
    )
