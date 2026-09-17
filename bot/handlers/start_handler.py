from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.clients.api_client import ApiClient
import bot.keyboards.admin_keyboards as admin_kb
import bot.keyboards.request_keyboard as req_kb
import bot.services.admin_service as admin_service
import bot.services.start_service as start_service
from bot.handlers.request_handler import show_main_menu

router = Router()


async def _get_start_keyboard(api_client: ApiClient, telegram_id: int):
    is_admin, _ = await admin_service.is_active_admin(api_client, telegram_id)
    if is_admin:
        return admin_kb.admin_menu_keyboard()
    return req_kb.START_KEYBOARD


@router.message(CommandStart())
async def handle_start_command(message: types.Message, api_client: ApiClient):
    telegram_id = message.from_user.id
    username = message.from_user.username

    is_registered, status_text = await start_service.get_user(api_client, telegram_id)

    if not is_registered and status_text == "Пользователь не найден":
        is_registered, status_text = await start_service.create_user(
            api_client,
            telegram_id,
            username,
        )
        if not is_registered:
            await message.answer(status_text or "Ошибка регистрации.")
            return

        await message.answer("Пользователь зарегистрирован.")
        await message.answer(
            "Выберите действие:",
            reply_markup=await _get_start_keyboard(api_client, telegram_id),
        )
        return

    if not is_registered:
        await message.answer(status_text or "Ошибка.")
        return

    await message.answer(
        "Выберите действие:",
        reply_markup=await _get_start_keyboard(api_client, telegram_id),
    )


@router.message(Command("help"))
async def handle_help_command(message: Message, api_client: ApiClient):
    is_admin, _ = await admin_service.is_active_admin(api_client, message.from_user.id)
    if is_admin:
        await message.answer(_get_admin_help_text())
    else:
        await message.answer(_get_user_help_text())

    await show_main_menu(message, api_client)


def _get_admin_help_text() -> str:
    return (
        "Команды администратора:\n"
        "/start - открыть меню администратора\n"
        "/help - справка\n"
        "/new_requests - новые заявки\n"
        "/in_progress - заявки в работе\n"
        "/today - заявки за сегодня"
    )


def _get_user_help_text() -> str:
    return (
        "Список команд:\n"
        "/start - запуск бота\n"
        "/help - список команд\n"
        "/request - создать заявку\n"
        "/cancel - отменить заявку\n"
        "/my_requests - мои заявки"
    )


@router.callback_query(F.data == "help")
async def handle_help_callback(callback: types.CallbackQuery, api_client: ApiClient):
    is_admin, _ = await admin_service.is_active_admin(
        api_client,
        callback.from_user.id,
    )
    await callback.answer()
    await callback.message.answer(
        _get_admin_help_text() if is_admin else _get_user_help_text()
    )
    await show_main_menu(callback.message, api_client)
                         