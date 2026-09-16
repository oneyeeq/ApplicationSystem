from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/health/")
async def get_health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
    except SQLAlchemyError:
        return JSONResponse(content={"status": "error"}, status_code=503)
    return JSONResponse(content={"status": "ok"})
