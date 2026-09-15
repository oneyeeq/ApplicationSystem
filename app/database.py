from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config import settings


def resolve_database_url(database_url: str) -> str:
    if not database_url.startswith("sqlite+aiosqlite:///./"):
        return database_url

    from pathlib import Path

    database_name = database_url.removeprefix("sqlite+aiosqlite:///./")
    database_path = Path(__file__).resolve().parent.parent / database_name
    return f"sqlite+aiosqlite:///{database_path}"


engine = create_async_engine(
    resolve_database_url(settings.DATABASE_URL),
    pool_pre_ping=True,
)

session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
