from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth_schemas import LoginRequest, LoginResponse
from app.services.auth_service import authenticate_admin
from app.database import get_db
from app.services.exceptions import AdminNotFoundError, AdminIsNotActiveError, PasswordNotValidError

router = APIRouter()

@router.post("/auth/login/", response_model=LoginResponse)
async def auth_login(request_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        response = await authenticate_admin(
            request_data,
            db,
        )
        return response
    except AdminNotFoundError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    except AdminIsNotActiveError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    except PasswordNotValidError:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")