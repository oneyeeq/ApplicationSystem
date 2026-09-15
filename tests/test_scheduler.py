from unittest.mock import AsyncMock, MagicMock

from scheduler.jobs import cleanup


async def test_scheduler_job_opens_session_and_returns_deleted_count(monkeypatch):
    session = AsyncMock()
    session_factory = MagicMock()
    session_factory.return_value.__aenter__.return_value = session
    session_factory.return_value.__aexit__.return_value = None

    monkeypatch.setattr(cleanup, "session_factory", session_factory)
    monkeypatch.setattr(
        cleanup,
        "delete_expired_closed_requests",
        AsyncMock(return_value=4),
    )

    result = await cleanup.cleanup_closed_requests()

    assert result == 4
    session_factory.assert_called_once_with()
    session.commit.assert_not_called()
