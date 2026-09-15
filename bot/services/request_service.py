from bot.clients.api_client import ApiClient
from bot.dtos import RequestCreateData, RequestData


async def can_start_request(api_client: ApiClient, telegram_id: int) -> tuple[bool, str | None]:
    result = await api_client.can_create_request(telegram_id)

    if result.error == "not_found":
        return False, "Сначала нужно зарегистрироваться."
    if result.error == "inactive":
        return False, "Вы заблокированы."
    if result.error in {"server_error", "unavailable"}:
        return False, "Сервис временно недоступен."
    if not result.allowed:
        return False, "Вы достигли лимита по активным заявкам."

    return True, None


async def submit_request(
    api_client: ApiClient,
    telegram_id: int,
    data: RequestCreateData,
) -> tuple[bool, str | None, RequestData | None]:
    request_data, status = await api_client.create_request(telegram_id, data)

    if status == "ok":
        return True, "Заявка отправлена.", request_data
    if status == "blocked":
        return False, "Вы заблокированы.", None
    if status == "limit":
        return False, "Вы достигли лимита по активным заявкам.", None
    if status == "not_found":
        return False, "Пользователь не найден. Сначала зарегистрируйтесь.", None
    if status == "validation_error":
        return False, "Данные заявки заполнены неверно.", None
    if status == "unavailable":
        return False, "Сервис временно недоступен. Попробуйте позже.", None

    return False, "Произошла ошибка. Попробуйте позже.", None


async def get_my_requests(
    api_client: ApiClient,
    telegram_id: int,
) -> tuple[list[RequestData] | None, str | None]:
    requests, status = await api_client.get_user_requests(telegram_id)
    if status == "ok":
        return requests or [], None
    if status == "not_found":
        return None, "Пользователь не найден."
    return None, "Сервис временно недоступен."
