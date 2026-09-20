from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.routes import admin_routes, request_routes, user_routes
from app.schemas.request_schemas import RequestCreate
from app.services.exceptions import (
    ActiveRequestLimitError,
    UserNotFoundError,
)


async def test_user_route_translates_missing_user():
    service = AsyncMock(side_effect=UserNotFoundError())
    original = user_routes.user_service.get_user_by_telegram_id
    user_routes.user_service.get_user_by_telegram_id = service
    try:
        with pytest.raises(HTTPException) as error:
            await user_routes.check_user_by_tg_id(1, AsyncMock())
    finally:
        user_routes.user_service.get_user_by_telegram_id = original

    assert error.value.status_code == 404


async def test_request_route_translates_limit_error(monkeypatch):
    monkeypatch.setattr(
        request_routes.request_service,
        "create_request",
        AsyncMock(side_effect=ActiveRequestLimitError()),
    )

    with pytest.raises(HTTPException) as error:
        await request_routes.create_request(
            1,
            RequestCreate(service_name="Сайт", phone_number="+100"),
            AsyncMock(),
        )

    assert error.value.status_code == 409


async def test_admin_route_returns_empty_list_when_no_active_admins(monkeypatch):
    monkeypatch.setattr(
        admin_routes.admin_service,
        "get_active_admins",
        AsyncMock(return_value=[]),
    )

    result = await admin_routes.get_active_admins(AsyncMock())

    assert result == []
