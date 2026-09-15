from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health/")
def get_health():
    return JSONResponse(content={"status": "ok"})
