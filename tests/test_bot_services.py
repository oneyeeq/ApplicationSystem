from unittest.mock import AsyncMock

from bot.services import request_service, start_service, admin_service
from bot.dtos import RequestData

def make_request(request_id: int, status: str) -> RequestData:
    return RequestData(
        id=request_id,
        service_name="Сайт",
        phone_number="+100",
        user_id=1,
        status=status,
        created_at="2026-09-14T00:00:00Z",
        updated_at="2026-09-14T00:00:00Z",
    )

async def test_start_service_translates_missing_user():
    api_client = AsyncMock()
    api_client.get_user.return_value = (None, "not_found")

    result = await start_service.get_user(api_client, 3001)

    assert result == (None, "Пользователь не найден")


async def test_start_service_returns_found_user():
    from bot.dtos import UserData

    user = UserData(id=1, tg_user_id=3001, username="tester", is_active=False, active_requests=0)
    api_client = AsyncMock()
    api_client.get_user.return_value = (user, "ok")

    found_user, status_text = await start_service.get_user(api_client, 3001)

    assert found_user == user
    assert found_user.is_active is False
    assert status_text is None


async def test_request_service_translates_api_limit():
    api_client = AsyncMock()
    api_client.create_request.return_value = (None, "limit")

    result = await request_service.submit_request(
        api_client,
        3002,
        {"service_name": "Сайт", "phone_number": "+10000000000"},
    )

    assert result == (False, "Вы достигли лимита по активным заявкам.", None)


async def test_request_service_returns_created_request():
    request_data = {"id": 10, "status": "новая"}
    api_client = AsyncMock()
    api_client.create_request.return_value = (request_data, "ok")

    result = await request_service.submit_request(api_client, 3003, {})

    assert result == (True, "Заявка отправлена.", request_data)


async def test_request_service_translates_blocked_user():
    api_client = AsyncMock()
    api_client.create_request.return_value = (None, "blocked")

    result = await request_service.submit_request(api_client, 3004, {})

    assert result == (False, "Вы заблокированы.", None)


async def test_request_service_returns_empty_user_request_list():
    api_client = AsyncMock()
    api_client.get_user_requests.return_value = (None, "ok")

    result = await request_service.get_my_requests(api_client, 3005)

    assert result == ([], None)


async def test_start_service_creates_user_successfully():
    api_client = AsyncMock()
    api_client.create_user.return_value = ({"id": 1}, "ok")

    result = await start_service.create_user(api_client, 3006, "user")

    assert result == (True, None)

async def test_get_requests_by_status_filters_correctly():
    requests = [
        make_request(1, "новая"),
        make_request(2, "в_процессе"),
        make_request(3, "новая"),
    ]
    api_client = AsyncMock()
    api_client.get_requests.return_value = (requests, "ok")

    result = await admin_service.get_requests_by_status(api_client, 1, "новая")

    assert result == (True, None, [make_request(1, "новая"), make_request(3, "новая")])

async def test_get_requests_by_status_filters_not_correctly():
    requests = [
        make_request(1, "завершена"),
        make_request(2, "в_процессе"),
        make_request(3, "завершена"),
    ]
    api_client = AsyncMock()
    api_client.get_requests.return_value = (requests, "ok")

    result = await admin_service.get_requests_by_status(api_client, 1, "новая")

    assert result == (True, None, [])

async def test_get_request_for_admin_correctly():
    api_client = AsyncMock()
    api_client.get_request.return_value = (make_request(5, "новая"), "ok")

    result = await admin_service.get_request_for_admin(api_client, 1, 5)

    assert result == (True, None, make_request(5, "новая"))

async def test_get_request_for_admin_not_correctly():
    api_client = AsyncMock()
    api_client.get_request.return_value = (None, "not_found")

    result = await admin_service.get_request_for_admin(api_client, 1, 6)

    assert result == (False, "Заявка не найдена", None)

async def test_update_request_status_accepted():
    api_client = AsyncMock()
    api_client.update_request_status.return_value = (make_request(7, "в_процессе"), "ok")

    result = await admin_service.update_request_status(api_client, 1, 7, "в_процессе")

    assert result == (True, "Заявка принята", make_request(7, "в_процессе"))

async def test_update_request_status_completed():
    api_client = AsyncMock()
    api_client.update_request_status.return_value = (make_request(7, "завершена"), "ok")

    result = await admin_service.update_request_status(api_client, 1, 7, "завершена")

    assert result == (True, "Заявка завершена", make_request(7, "завершена"))

async def test_update_request_status_rejected():
    api_client = AsyncMock()
    api_client.update_request_status.return_value = (make_request(7, "отклонена"), "ok")

    result = await admin_service.update_request_status(api_client, 1, 7, "отклонена")

    assert result == (True, "Заявка отклонена", make_request(7, "отклонена"))

async def test_get_today_requests_service_unavailable():
    api_client = AsyncMock()
    api_client.get_requests.return_value = (None, "error")

    result = await admin_service.get_today_requests(api_client, 1)

    assert result == (False, "Сервис временно недоступен", [])
