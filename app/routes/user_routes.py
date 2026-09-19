from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.services import user_service
from app.services.exceptions import UserHasRequestsError, UserNotFoundError
from app.dependencies.service_or_admin_auth import verify_service_token_or_admin

router = APIRouter(dependencies=[Depends(verify_service_token_or_admin)])
DbSession = Annotated[AsyncSession, Depends(get_db)]

@router.get("/users/by-telegram/{telegram_id}", response_model=UserResponse)
async def check_user_by_tg_id(telegram_id: int, db: DbSession):
    try:
        return await user_service.get_user_by_telegram_id(db, telegram_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

@router.get("/users/", response_model=list[UserResponse])
async def get_users(db: DbSession):
    return await user_service.list_users(db)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: DbSession):
    try:
        return await user_service.get_user_by_id(db, user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.post("/users/", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: DbSession):
    try:
        return await user_service.create_user(db, user_data)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким Telegram ID уже существует",
        )
@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    user_id: int,
    db: DbSession,
):
    try:
        return await user_service.update_user(db, user_id, user_data)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

@router.get("/users/by-telegram/{telegram_id}/can-create-request")
async def can_create_request(telegram_id: int, db: DbSession):
    try:
        return await user_service.can_create_request(db, telegram_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: DbSession):
    try:
        await user_service.delete_user(db, user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except UserHasRequestsError:
        raise HTTPException(status_code=409, detail="Нельзя удалить пользователя — у него есть заявки")
    return {"message": "Пользователь удалён"}


