from unittest.mock import AsyncMock

from bot.handlers import admin_navigation
from bot.dtos import RequestData


def make_request(request_id: int) -> RequestData:
    return RequestData(
        id=request_id,
        service_name="Сайт",
        phone_number="+100",
        user_id=1,
        status="новая",
        created_at="2026-09-14T00:00:00Z",
        updated_at="2026-09-14T00:00:00Z",
    )


async def test_navigation_returns_next_request(monkeypatch):
    requests = [make_request(1), make_request(2), make_request(3)]
    getter = AsyncMock(return_value=(True, None, requests))
    monkeypatch.setattr(
        admin_navigation.admin_service,
        "get_requests_by_status",
        getter,
    )

    result = await admin_navigation.get_adjacent_request(
        AsyncMock(),
        telegram_id=4001,
        request_id=2,
        direction=1,
        status_to_find="новая",
    )

    assert result == (True, None, make_request(3))
    getter.assert_awaited_once()


async def test_navigation_rejects_previous_from_first_request(monkeypatch):
    getter = AsyncMock(return_value=(True, None, [make_request(1)]))
    monkeypatch.setattr(
        admin_navigation.admin_service,
        "get_requests_by_status",
        getter,
    )

    result = await admin_navigation.get_adjacent_request(
        AsyncMock(),
        telegram_id=4002,
        request_id=1,
        direction=-1,
        status_to_find="новая",
    )

    assert result == (False, "Это первая заявка", None)
