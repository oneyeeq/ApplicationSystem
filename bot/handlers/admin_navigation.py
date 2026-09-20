import bot.services.admin_service as admin_service
from bot.clients.api_client import ApiClient
from bot.services.admin_service import RequestListGetter


async def _get_adjacent_request(
    api_client: ApiClient,
    telegram_id: int,
    request_id: int,
    direction: int,
    request_list_getter: RequestListGetter,
) -> tuple[bool, str | None, dict | None]:
    is_success, error_text, requests = await request_list_getter(api_client, telegram_id)
    if not is_success:
        return False, error_text, None
    if not requests:
        return False, "Заявки не найдены", None

    current_index = next(
        (index for index, request in enumerate(requests) if request.id == request_id),
        None,
    )
    if current_index is None:
        return False, "Список заявок обновился", None

    adjacent_index = current_index + direction
    if adjacent_index < 0:
        return False, "Это первая заявка", None
    if adjacent_index >= len(requests):
        return False, "Это последняя заявка", None
    return True, None, requests[adjacent_index]


async def get_adjacent_request(
    api_client: ApiClient,
    telegram_id: int,
    request_id: int,
    direction: int,
    status_to_find: str,
) -> tuple[bool, str | None, dict | None]:
    async def _by_status(client: ApiClient, tid: int):
        return await admin_service.get_requests_by_status(client, tid, status_to_find)

    return await _get_adjacent_request(api_client, telegram_id, request_id, direction, _by_status)


async def get_adjacent_today_request(
    api_client: ApiClient,
    telegram_id: int,
    request_id: int,
    direction: int,
) -> tuple[bool, str | None, dict | None]:
    return await _get_adjacent_request(
        api_client, telegram_id, request_id, direction, admin_service.get_today_requests
    )
