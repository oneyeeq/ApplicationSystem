"""Shared database fixtures for service-level tests."""

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import (
    models as _models,  # noqa: F401 -- registers all models on Base.metadata before create_all
)
from app.database import Base


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        # SQLite ignores FOREIGN KEY constraints (ondelete=RESTRICT/CASCADE)
        # unless this pragma is set per-connection; Postgres enforces them
        # by default, so without this the test DB silently diverges from prod.
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

    await engine.dispose()
