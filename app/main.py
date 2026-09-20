from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import settings
from app.database import engine
from app.rate_limiter import limiter
from app.routes.health_routes import router as health_router
from app.routes.admin_routes import router as admin_router
from app.routes.request_routes import router as request_router
from app.routes.user_routes import router as user_router
from app.routes.auth_routes import router as auth_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title=settings.API_TITLE,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(admin_router)
app.include_router(request_router)
app.include_router(user_router)
app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
