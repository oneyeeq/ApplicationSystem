from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.request_schemas import RequestCreate, RequestResponse, RequestUpdate
from app.services import request_service
from app.dependencies.service_auth import verify_service_token
from app.services.notification_service import (
    notify_admins_about_request,
    notify_user_about_status,
)
from app.services.exceptions import (
    ActiveRequestLimitError,
    InactiveUserError,
    RequestNotFoundError,
    UserNotFoundError,
    RequestAlreadyClosedError,
    RequestTransitionNotAllowedError,
)

router = APIRouter(dependencies=[Depends(verify_service_token)])


@router.post("/requests/{telegram_id}", response_model=RequestResponse)
async def create_request(
    telegram_id: int, request_data: RequestCreate, db: AsyncSession = Depends(get_db)
):  
    try:
        request = await request_service.create_request(db, telegram_id, request_data)
        await notify_admins_about_request(request.id)
        return request
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except InactiveUserError:
        raise HTTPException(status_code=403, detail="Пользователь заблокирован")
    except ActiveRequestLimitError:
        raise HTTPException(status_code=409, detail="Достигнут лимит активных заявок")


@router.get("/requests/", response_model=list[RequestResponse])
async def get_requests(db: AsyncSession = Depends(get_db)):
    return await request_service.list_requests(db)


@router.get("/requests/by-telegram/{telegram_id}", response_model=list[RequestResponse])
async def get_user_requests(telegram_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await request_service.list_user_requests(db, telegram_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.get("/requests/{request_id}", response_model=RequestResponse)
async def get_request(request_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await request_service.get_request(db, request_id)
    except RequestNotFoundError:
        raise HTTPException(status_code=404, detail="Заявка не найдена")


@router.put("/requests/{request_id}", response_model=RequestResponse)
async def update_request(
    request_id: int, request_data: RequestUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        request = await request_service.update_request(db, request_id, request_data)
        await notify_user_about_status(request)
        return request
    except RequestAlreadyClosedError:
        raise HTTPException(status_code=409, detail="Заявка уже закрыта или отклонена")
    except RequestTransitionNotAllowedError:
        raise HTTPException(status_code=409, detail="Заявка не может быть изменена")
    except RequestNotFoundError:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.delete("/requests/{request_id}")
async def delete_request(request_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await request_service.delete_request(db, request_id)
    except RequestNotFoundError:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"message": "Заявка удалена"}
