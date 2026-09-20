from unittest.mock import AsyncMock

from app.services import notification_service


async def test_missing_admins_are_treated_as_empty_notification_list(monkeypatch):
    monkeypatch.setattr(
        notification_service.admin_service,
        "get_active_admins",
        AsyncMock(return_value=[]),
    )

    result = await notification_service._get_active_admins()

    assert result == []
