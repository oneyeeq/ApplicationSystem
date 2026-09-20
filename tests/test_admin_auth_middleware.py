from unittest.mock import AsyncMock

from aiogram.types import CallbackQuery, Message

import bot.middlewares.admin_auth as admin_auth_module
from bot.middlewares.admin_auth import AdminAuthMiddleware


async def test_middleware_rejects_non_admin_callback(monkeypatch):
    monkeypatch.setattr(
        admin_auth_module,
        "is_active_admin",
        AsyncMock(return_value=(False, "Доступ запрещён")),
    )

    middleware = AdminAuthMiddleware()
    handler = AsyncMock()
    event = AsyncMock()
    event.__class__ = CallbackQuery
    event.from_user.id = 111
    data = {"api_client": AsyncMock()}

    await middleware(handler, event, data)

    assert handler.called is False
    event.answer.assert_awaited_once_with("Доступ запрещён", show_alert=True)


async def test_middleware_rejects_non_admin_message(monkeypatch):
    monkeypatch.setattr(
        admin_auth_module,
        "is_active_admin",
        AsyncMock(return_value=(False, "Доступ запрещён")),
    )

    middleware = AdminAuthMiddleware()
    handler = AsyncMock()
    event = AsyncMock()
    event.__class__ = Message
    event.from_user.id = 111
    data = {"api_client": AsyncMock()}

    await middleware(handler, event, data)

    assert handler.called is False
    event.answer.assert_awaited_once_with("Доступ запрещён")


async def test_middleware_accepts_is_admin(monkeypatch):
    monkeypatch.setattr(
        admin_auth_module,
        "is_active_admin",
        AsyncMock(return_value=(True, None)),
    )

    middleware = AdminAuthMiddleware()
    handler = AsyncMock(return_value="test_result")
    event = AsyncMock()
    event.__class__ = CallbackQuery
    event.from_user.id = 111
    data = {"api_client": AsyncMock()}

    result = await middleware(handler, event, data)

    handler.assert_awaited_once_with(event, data)
    event.answer.assert_not_called()
    assert result == "test_result"
