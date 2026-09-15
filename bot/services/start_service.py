from bot.clients.api_client import ApiClient


async def get_user(api_client: ApiClient, telegram_id: int) -> tuple[bool, str | None]:
    _, status = await api_client.get_user(telegram_id)
    if status == "ok":
        return True, None
    if status == "not_found":
        return False, "Пользователь не найден"
    return False, "Ошибка сервиса"


async def create_user(
    api_client: ApiClient,
    telegram_id: int,
    username: str | None,
) -> tuple[bool, str | None]:
    _, status = await api_client.create_user(telegram_id, username)
    if status == "ok":
        return True, None
    return False, "Ошибка регистрации"