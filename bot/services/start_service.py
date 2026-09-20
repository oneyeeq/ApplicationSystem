from bot.clients.api_client import ApiClient
from bot.dtos import UserData


async def get_user(api_client: ApiClient, telegram_id: int) -> tuple[UserData | None, str | None]:
    user, status = await api_client.get_user(telegram_id)
    if status == "ok":
        return user, None
    if status == "not_found":
        return None, "Пользователь не найден"
    return None, "Ошибка сервиса"


async def create_user(
    api_client: ApiClient,
    telegram_id: int,
    username: str | None,
) -> tuple[bool, str | None]:
    _, status = await api_client.create_user(telegram_id, username)
    if status == "ok":
        return True, None
    return False, "Ошибка регистрации"
