from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.clients.api_client import ApiClient
from bot.services.admin_service import is_active_admin


class AdminAuthMiddleware(BaseMiddleware):
    """Проверяет is_active_admin один раз на входящее событие.

    Регистрируется на admin-роутере, чтобы дальше по цепочке (сервисы,
    вызываемые из хендлеров) не нужно было перепроверять права заново.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        api_client: ApiClient = data["api_client"]
        telegram_id = event.from_user.id

        is_admin, error_text = await is_active_admin(api_client, telegram_id)
        if not is_admin:
            error_message = error_text or "Доступ запрещён"
            if isinstance(event, CallbackQuery):
                await event.answer(error_message, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(error_message)
            return None

        return await handler(event, data)
