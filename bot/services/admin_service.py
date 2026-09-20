from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from datetime import timezone as datetime_timezone
from zoneinfo import ZoneInfo

from bot.clients.api_client import ApiClient
from bot.dtos import AdminData, RequestData
from config import settings
from enums import StatusEnum

RequestListGetter = Callable[
    [ApiClient, int],
    Awaitable[tuple[bool, str | None, list[RequestData]]],
]

timezone = ZoneInfo(settings.TIMEZONE)


def get_today_range() -> tuple[datetime, datetime]:
    current_time = datetime.now(timezone)
    today_start = current_time.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    tomorrow_start = today_start + timedelta(days=1)
    return today_start, tomorrow_start


async def get_today_requests(
    api_client: ApiClient, telegram_id: int
) -> tuple[bool, str | None, list[RequestData]]:
    requests, status = await api_client.get_requests()
    if status != "ok":
        return False, "Сервис временно недоступен", []
    if requests is None:
        return True, "Заявок за сегодня нет", []
    today_start, tomorrow_start = get_today_range()
    today_requests = []
    for request in requests:
        created_datetime = request.created_at
        updated_datetime = request.updated_at
        if created_datetime.tzinfo is None:
            created_datetime = created_datetime.replace(tzinfo=datetime_timezone.utc)
        if updated_datetime.tzinfo is None:
            updated_datetime = updated_datetime.replace(tzinfo=datetime_timezone.utc)
        created_datetime = created_datetime.astimezone(timezone)
        updated_datetime = updated_datetime.astimezone(timezone)
        if (
            today_start <= created_datetime < tomorrow_start
            or today_start <= updated_datetime < tomorrow_start
        ):
            today_requests.append(request)
    return True, None, today_requests


async def get_active_admins(api_client: ApiClient) -> tuple[bool, str | None, list[AdminData]]:
    admins, status = await api_client.get_active_admins()
    if status == "ok":
        return True, None, admins or []
    if status == "not_found":
        return False, "Не найдено", []
    return False, "Ошибка сервера", []


async def is_active_admin(
    api_client: ApiClient,
    telegram_id: int,
) -> tuple[bool, str | None]:
    is_success, error_text, admins = await get_active_admins(api_client)
    if not is_success:
        return False, "Сервис временно недоступен"
    if not any(admin.tg_admin_id == telegram_id for admin in admins):
        return False, "Доступ запрещён"
    return True, None


async def get_request_for_admin(
    api_client: ApiClient,
    telegram_id: int,
    request_id: int,
) -> tuple[bool, str | None, RequestData | None]:
    request_data, status = await api_client.get_request(request_id)
    if status == "not_found":
        return False, "Заявка не найдена", None
    if status != "ok":
        return False, "Сервис временно недоступен", None
    return True, None, request_data


async def update_request_status(
    api_client: ApiClient,
    telegram_id: int,
    request_id: int,
    new_status: str,
) -> tuple[bool, str | None, RequestData | None]:
    request_data, status = await api_client.update_request_status(
        request_id,
        new_status,
    )
    if status == "ok":
        status_messages = {
            StatusEnum.IN_PROGRESS.value: "Заявка принята",
            StatusEnum.COMPLETED.value: "Заявка завершена",
            StatusEnum.REJECTED.value: "Заявка отклонена",
        }
        message = status_messages.get(new_status, "Статус заявки изменён")
        return True, message, request_data
    if status == "not_found":
        return False, "Заявка не найдена", None
    if status == "unavailable":
        return False, "Сервис временно недоступен", None
    return False, "Ошибка", None


async def get_requests_by_status(
    api_client: ApiClient,
    telegram_id: int,
    status_to_find: str,
) -> tuple[bool, str | None, list[RequestData]]:
    requests, status = await api_client.get_requests()
    if status != "ok":
        return False, "Сервис временно недоступен", []

    filtered_requests = [
        request for request in (requests or []) if request.status == status_to_find
    ]

    return True, None, filtered_requests


async def get_new_requests(
    api_client: ApiClient,
    telegram_id: int,
) -> tuple[bool, str | None, list[RequestData]]:
    return await get_requests_by_status(api_client, telegram_id, StatusEnum.NEW.value)


async def get_in_progress_requests(
    api_client: ApiClient,
    telegram_id: int,
) -> tuple[bool, str | None, list[RequestData]]:
    return await get_requests_by_status(api_client, telegram_id, StatusEnum.IN_PROGRESS.value)


async def _get_first_request(
    api_client: ApiClient,
    telegram_id: int,
    request_list_getter: RequestListGetter,
    empty_message: str,
) -> tuple[bool, str | None, RequestData | None]:
    is_success, error_text, requests = await request_list_getter(
        api_client,
        telegram_id,
    )

    if not is_success:
        return False, error_text, None

    if not requests:
        return True, empty_message, None

    return True, None, requests[0]


async def get_first_new_request(
    api_client: ApiClient,
    telegram_id: int,
) -> tuple[bool, str | None, RequestData | None]:
    return await _get_first_request(
        api_client,
        telegram_id,
        get_new_requests,
        "Новых заявок нет",
    )


async def get_first_in_progress_request(
    api_client: ApiClient,
    telegram_id: int,
) -> tuple[bool, str | None, RequestData | None]:
    return await _get_first_request(
        api_client,
        telegram_id,
        get_in_progress_requests,
        "Заявок в работе нет",
    )
