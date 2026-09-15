from unittest.mock import AsyncMock

from bot.services import request_service, start_service


async def test_start_service_translates_missing_user():
    api_client = AsyncMock()
    api_client.get_user.return_value = (None, "not_found")

    result = await start_service.get_user(api_client, 3001)

    assert result == (False, "Пользователь не найден")


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
