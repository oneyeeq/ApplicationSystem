from fastapi import Response, Cookie
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.auth_schemas import LoginRequest, LoginResponse
from app.services.auth_service import (authenticate_admin,
                                       refresh_access_token,
                                       revoke_refresh_token,
                                       )
from app.database import get_db
from app.services.exceptions import (
    AdminNotFoundError,
    AdminIsNotActiveError,
    PasswordNotValidError,
    RefreshTokenInvalidError,
    RefreshTokenExpiredError,
)

router = APIRouter()

@router.post("/auth/login/", response_model=LoginResponse)
async def auth_login(
    request_data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
        login_response, raw_refresh_token = await authenticate_admin(
            request_data,
            db
        )
        response.set_cookie(
            key="refresh_token",
            value=raw_refresh_token,
            httponly=True,
            samesite="lax",
        )
        return login_response
    except AdminNotFoundError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    except AdminIsNotActiveError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    except PasswordNotValidError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

@router.post("/auth/refresh/", response_model=LoginResponse)
async def auth_refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Токен отсутствует")
    try:
        new_access_token, new_raw_refresh_token = await refresh_access_token(refresh_token, db)
        response.set_cookie(
            key="refresh_token",
            value=new_raw_refresh_token,
            httponly=True,
            samesite="lax",
        )
        return LoginResponse(access_token=new_access_token, token_type="bearer")
    except RefreshTokenInvalidError:
        raise HTTPException(status_code=401, detail="Неправильный токен")
    except RefreshTokenExpiredError:
        raise HTTPException(status_code=401, detail="Токен истек")

@router.post("/auth/logout/")
async def auth_logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token is not None:
        await revoke_refresh_token(refresh_token, db)
    response.delete_cookie("refresh_token")
    return {"message": "Вы вышли из системы"}
