import hmac

from fastapi import Header, HTTPException, status

from config import settings


async def verify_service_token(x_service_token: str | None = Header(default=None)):
    if x_service_token is None or not hmac.compare_digest(x_service_token, settings.SERVICE_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный сервисный токен",
        )
