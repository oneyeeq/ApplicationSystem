from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.admin_schemas import (
    AdminCreate,
    AdminNotificationResponse,
    AdminResponse,
)
from app.models.admin_model import Admin
from app.services.exceptions import AdminAlreadyExistsError, AdminNotFoundError
from app.services import admin_service
from app.dependencies.auth import get_current_admin

router = APIRouter()

@router.get("/admins/active", response_model=list[AdminNotificationResponse])
async def get_active_admins(db: AsyncSession = Depends(get_db)):
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
