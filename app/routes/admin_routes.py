from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.dependencies.service_auth import verify_service_token
from app.models.admin_model import Admin
from app.schemas.admin_schemas import (
    AdminCreate,
    AdminNotificationResponse,
    AdminResponse,
    AdminUpdate,
)
from app.services import admin_service
from app.services.exceptions import (
    AdminAlreadyExistsError,
    AdminNotFoundError,
    AdminSelfDeleteError,
)

router = APIRouter()


@router.get("/admins/active", response_model=list[AdminNotificationResponse])
async def get_active_admins(
    db: AsyncSession = Depends(get_db), _: None = Depends(verify_service_token)
):
    try:
        return await admin_service.get_active_admins(db)
    except AdminNotFoundError:
        raise HTTPException(status_code=404, detail="Активные админы не найдены")


@router.post("/admins/", response_model=AdminResponse)
async def create_admin(
    admin_data: AdminCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    try:
        return await admin_service.create_admin(admin_data, db)
    except AdminAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Админ уже существует")


@router.get("/admins/", response_model=list[AdminResponse])
async def list_admins(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return await admin_service.get_admins(db)


@router.put("/admins/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: int,
    admin_data: AdminUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    try:
        return await admin_service.update_admin(db, admin_id, admin_data)
    except AdminNotFoundError:
        raise HTTPException(status_code=404, detail="Админ не найден")
    except AdminAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Админ с таким tg_admin_id уже существует")


@router.delete("/admins/{admin_id}")
async def delete_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    try:
        await admin_service.delete_admin(db, admin_id, admin.id)
    except AdminNotFoundError:
        raise HTTPException(status_code=404, detail="Админ не найден")
    except AdminSelfDeleteError:
        raise HTTPException(status_code=409, detail="Нельзя удалить самого себя")
    return {"message": "Админ удалён"}
