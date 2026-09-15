from bot.clients.api_client import ApiClient
import bot.services.admin_service as admin_service


async def get_adjacent_request(
    api_client: ApiClient,
    telegram_id: int,
    request_id: int,
    direction: int,
    status_to_find: str,
) -> tuple[bool, str | None, dict | None]:
    is_success, error_text, requests = await admin_service.get_requests_by_status(
        api_client, telegram_id, status_to_find
    )
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


async def get_adjacent_today_request(
    api_client: ApiClient,
    telegram_id: int,
    request_id: int,
    direction: int,
) -> tuple[bool, str | None, dict | None]:
    is_success, error_text, requests = await admin_service.get_today_requests(
        api_client, telegram_id
    )
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
