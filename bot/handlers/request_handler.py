from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

import bot.keyboards.admin_keyboards as admin_kb
import bot.keyboards.request_keyboard as kb
import bot.services.admin_service as admin_service
import bot.services.request_service as request_service
from bot.clients.api_client import ApiClient
from bot.presenters.user_requests import format_user_requests

router = Router()

AVAILABLE_SERVICE_NAMES = ["Сайт", "Скрипт", "Бот"]


async def show_main_menu(
    message: Message,
    api_client: ApiClient,
    telegram_id: int,
    text: str = "Выберите действие:",
):
    is_admin, _ = await admin_service.is_active_admin(
        api_client,
        telegram_id,
    )
    reply_markup = admin_kb.admin_menu_keyboard() if is_admin else kb.START_KEYBOARD
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await message.answer("Выберите действие:", reply_markup=reply_markup)


async def remove_inline_keyboard(callback: CallbackQuery) -> None:
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise


class RequestForm(StatesGroup):
    service_name = State()
    phone_number = State()


@router.message(Command("request"))
async def handle_request_command(
    message: Message,
    state: FSMContext,
    api_client: ApiClient,
):
    is_admin, _ = await admin_service.is_active_admin(api_client, message.from_user.id)
    if is_admin:
        await show_main_menu(
            message, api_client, message.from_user.id, "Администратору этот сценарий недоступен."
        )
        return

    is_allowed, status_text = await request_service.can_start_request(
        api_client,
        message.from_user.id,
    )
    if not is_allowed:
        await show_main_menu(
            message, api_client, message.from_user.id, status_text or "Сервис временно недоступен."
        )
        return

    await state.set_state(RequestForm.service_name)
    await message.answer("Выберите услугу", reply_markup=kb.SERVICES_KEYBOARD)


@router.callback_query(F.data == "request")
async def handle_request_callback(
    callback: CallbackQuery,
    state: FSMContext,
    api_client: ApiClient,
):
    telegram_id = callback.from_user.id
    is_admin, _ = await admin_service.is_active_admin(api_client, telegram_id)
    if is_admin:
        await remove_inline_keyboard(callback)
        await callback.answer("Администратору этот сценарий недоступен.", show_alert=True)
        await show_main_menu(callback.message, api_client, telegram_id)
        return

    is_allowed, status_text = await request_service.can_start_request(api_client, telegram_id)

    if not is_allowed:
        await remove_inline_keyboard(callback)
        await callback.answer()
        await show_main_menu(
            callback.message, api_client, telegram_id, status_text or "Сервис временно недоступен."
        )
        return

    await state.set_state(RequestForm.service_name)
    await remove_inline_keyboard(callback)
    await callback.message.answer("Выберите услугу", reply_markup=kb.SERVICES_KEYBOARD)
    await callback.answer()


@router.callback_query(F.data == "my_requests")
async def handle_my_requests(callback: CallbackQuery, api_client: ApiClient):
    is_admin, _ = await admin_service.is_active_admin(
        api_client,
        callback.from_user.id,
    )
    if is_admin:
        await callback.answer("Этот раздел доступен только пользователям.", show_alert=True)
        return

    requests, error_text = await request_service.get_my_requests(
        api_client,
        callback.from_user.id,
    )

    if requests is None:
        await callback.answer(error_text, show_alert=True)
        return

    if not requests:
        await callback.answer("У вас пока нет заявок.")
        return

    await callback.answer()
    await callback.message.answer(
        format_user_requests(requests),
        reply_markup=kb.BACK_TO_MENU_KEYBOARD,
    )


@router.message(Command("my_requests"))
async def handle_my_requests_command(message: Message, api_client: ApiClient):
    is_admin, _ = await admin_service.is_active_admin(
        api_client,
        message.from_user.id,
    )
    if is_admin:
        await message.answer("Раздел «Мои заявки» доступен только пользователям.")
        return

    requests, error_text = await request_service.get_my_requests(
        api_client,
        message.from_user.id,
    )

    if requests is None:
        await message.answer(error_text or "Сервис временно недоступен.")
        return

    if not requests:
        await message.answer("У вас пока нет заявок.")
        return

    await message.answer(
        format_user_requests(requests),
        reply_markup=kb.BACK_TO_MENU_KEYBOARD,
    )


@router.message(F.text == "Отменить заявку")
async def handle_cancel_request_message(
    message: Message,
    state: FSMContext,
    api_client: ApiClient,
):
    await _cancel_and_show_menu(message, state, api_client, "Заявка отменена.")


@router.message(Command("cancel"))
async def handle_cancel_command(
    message: Message,
    state: FSMContext,
    api_client: ApiClient,
):
    await _cancel_and_show_menu(message, state, api_client, "Заявка отменена.")


async def _cancel_and_show_menu(
    message: Message,
    state: FSMContext,
    api_client: ApiClient,
    text: str,
) -> None:
    await state.clear()
    is_admin, _ = await admin_service.is_active_admin(
        api_client,
        message.from_user.id,
    )
    await show_main_menu(
        message,
        api_client,
        message.from_user.id,
        "Выберите действие:" if is_admin else text,
    )


@router.message(RequestForm.service_name, F.text)
async def handle_service_choice(message: Message, state: FSMContext):
    service_name = message.text.strip()
    if not service_name:
        await message.answer(
            "Пожалуйста, выберите услугу из списка.",
            reply_markup=kb.SERVICES_KEYBOARD,
        )
        return

    if service_name not in AVAILABLE_SERVICE_NAMES:
        await message.answer(
            "Такой услуги нет. Выберите из предложенных:",
            reply_markup=kb.SERVICES_KEYBOARD,
        )
        return

    await state.update_data(service_name=service_name)
    await state.set_state(RequestForm.phone_number)
    await message.answer("Введите свой номер телефона", reply_markup=kb.PHONE_KEYBOARD)


@router.message(RequestForm.phone_number, F.contact)
async def handle_phone_contact(message: Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer(
            "Пожалуйста, отправьте свой номер.",
            reply_markup=kb.PHONE_KEYBOARD,
        )
        return

    await state.update_data(phone_number=message.contact.phone_number)
    request_data = await state.get_data()
    await message.answer(
        f"Услуга: {request_data['service_name']}\n"
        f"Телефон: {request_data['phone_number']}\n"
        "Отправить заявку?",
        reply_markup=kb.SUBMIT_KEYBOARD,
    )


@router.callback_query(F.data == "submit")
async def handle_submit_request(
    callback: CallbackQuery,
    state: FSMContext,
    api_client: ApiClient,
):
    telegram_id = callback.from_user.id
    await remove_inline_keyboard(callback)

    request_data = await state.get_data()
    if not request_data.get("service_name") or not request_data.get("phone_number"):
        await state.clear()
        await callback.answer("Сессия заявки устарела.", show_alert=True)
        await show_main_menu(callback.message, api_client, telegram_id, "Сессия заявки устарела.")
        return

    is_success, status_text, _ = await request_service.submit_request(
        api_client,
        telegram_id,
        request_data,
    )
    await callback.answer()

    if not is_success:
        await state.clear()
        await show_main_menu(
            callback.message,
            api_client,
            telegram_id,
            status_text or "Произошла ошибка. Попробуйте позже.",
        )
        return

    await state.clear()
    await show_main_menu(
        callback.message, api_client, telegram_id, status_text or "Заявка отправлена."
    )


@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery, api_client: ApiClient):
    await callback.answer()
    await remove_inline_keyboard(callback)
    is_admin, _ = await admin_service.is_active_admin(api_client, callback.from_user.id)
    reply_markup = admin_kb.admin_menu_keyboard() if is_admin else kb.START_KEYBOARD
    await callback.message.answer("Выберите действие:", reply_markup=reply_markup)


@router.callback_query(F.data == "cancelrequest")
async def handle_cancel_request_callback(
    callback: CallbackQuery,
    state: FSMContext,
    api_client: ApiClient,
):
    await state.clear()
    await remove_inline_keyboard(callback)
    await callback.answer()
    await show_main_menu(callback.message, api_client, callback.from_user.id, "Заявка отменена.")
