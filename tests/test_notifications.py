from unittest.mock import AsyncMock

from app.services import notification_service
from app.services.exceptions import AdminNotFoundError


async def test_missing_admins_are_treated_as_empty_notification_list(monkeypatch):
    monkeypatch.setattr(
        notification_service.admin_service,
        "get_active_admins",
        AsyncMock(side_effect=AdminNotFoundError()),
    )

    result = await notification_service._get_active_admins()

    assert result == []
