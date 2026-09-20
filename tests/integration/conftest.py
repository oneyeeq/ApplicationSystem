from collections.abc import AsyncIterator

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import Base, get_db
from app.main import app
from app.rate_limiter import limiter


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncSession]:
    # the limiter is a module-level singleton shared across every test in
    # the run; without resetting it, tests calling /auth/login/ repeatedly
    # (e.g. wrong-password cases) would start tripping the rate limit
    # depending on test order, not on anything the test itself does.
    limiter.reset()

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    async with engine.begin() as session:
        await session.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client, session_factory

    app.dependency_overrides.clear()
    await engine.dispose()
