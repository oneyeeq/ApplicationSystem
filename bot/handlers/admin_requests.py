from collections.abc import Awaitable, Callable

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import bot.keyboards.admin_keyboards as kb
import bot.services.admin_service as admin_service
from bot.clients.api_client import ApiClient
from bot.dtos import RequestData
from bot.handlers.admin_navigation import (
    get_adjacent_request,
    get_adjacent_today_request,
)
from bot.handlers.admin_presenter import (
    format_request_text,
    get_today_request_keyboard,
)
from enums import StatusEnum

router = Router()

RenderAfterUpdate = Callable[
    [CallbackQuery, ApiClient, RequestData | None],
    Awaitable[None],
]


async def _send_first_admin_request(
    message: Message,
    request_data: dict | None,
    empty_text: str,
    keyboard_factory,
) -> None:
    if request_data is None:
        await message.answer(empty_text)
        return

    await message.answer(
        format_request_text(request_data),
        reply_markup=keyboard_factory(request_data.id),
    )


async def _edit_to_first_new_request(
    callback: CallbackQuery,
    api_client: ApiClient,
) -> bool:
    is_success, error_text, next_request = await admin_service.get_first_new_request(
        api_client,
        callback.from_user.id,
    )

    if not is_success:
        await callback.message.edit_text(
            error_text or "Сервис временно недоступен.",
            reply_markup=kb.admin_menu_keyboard(),
        )
        return False

    if next_request is None:
        await callback.message.edit_text(
            "Выберите действие:",
            reply_markup=kb.admin_menu_keyboard(),
        )
        return False

    await callback.message.edit_text(
        format_request_text(next_request),
        reply_markup=kb.admin_new_request_keyboard(next_request.id),
    )
    return True


async def _edit_to_first_in_progress_request(
    callback: CallbackQuery,
    api_client: ApiClient,
) -> bool:
    is_success, error_text, next_request = await admin_service.get_first_in_progress_request(
        api_client,
        callback.from_user.id,
    )

    if not is_success:
        await callback.message.edit_text(
            error_text or "Сервис временно недоступен.",
            reply_markup=kb.admin_menu_keyboard(),
        )
        return False

    if next_request is None:
        await callback.message.edit_text(
            "Выберите действие:",
            reply_markup=kb.admin_menu_keyboard(),
        )
        return False

    await callback.message.edit_text(
        format_request_text(next_request),
        reply_markup=kb.admin_in_progress_request_keyboard(next_request.id),
    )
    return True


async def _update_request_status_from_callback(
    callback: CallbackQuery,
    api_client: ApiClient,
    new_status: str,
    render_after: RenderAfterUpdate,
) -> None:
    request_id = int(callback.data.split(":", maxsplit=1)[1])
    is_success, status_text, request_data = await admin_service.update_request_status(
        api_client,
        callback.from_user.id,
        request_id,
        new_status,
    )

    if not is_success:
        await callback.answer(status_text, show_alert=True)
        return

    await callback.answer(status_text)
    await render_after(callback, api_client, request_data)


async def _render_first_new_request(
    callback: CallbackQuery,
    api_client: ApiClient,
    request_data: RequestData | None,
) -> None:
    await _edit_to_first_new_request(callback, api_client)


async def _render_first_in_progress_request(
    callback: CallbackQuery,
    api_client: ApiClient,
    request_data: RequestData | None,
) -> None:
    await _edit_to_first_in_progress_request(callback, api_client)


async def _render_admin_menu(
    callback: CallbackQuery,
    api_client: ApiClient,
    request_data: RequestData | None,
) -> None:
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=kb.admin_menu_keyboard(),
    )


async def _render_today_request(
    callback: CallbackQuery,
    api_client: ApiClient,
    request_data: RequestData | None,
) -> None:
    await callback.message.edit_text(
        format_request_text(request_data),
        reply_markup=get_today_request_keyboard(request_data),
    )


async def update_new_request_status_from_callback(
    callback: CallbackQuery,
    api_client: ApiClient,
    new_status: str,
) -> None:
    await _update_request_status_from_callback(
        callback, api_client, new_status, _render_first_new_request
    )


async def update_in_progress_request_status_from_callback(
    callback: CallbackQuery,
    api_client: ApiClient,
    new_status: str,
) -> None:
    await _update_request_status_from_callback(
        callback, api_client, new_status, _render_first_in_progress_request
    )


async def update_notification_request_status_from_callback(
    callback: CallbackQuery,
    api_client: ApiClient,
    new_status: str,
) -> None:
    await _update_request_status_from_callback(callback, api_client, new_status, _render_admin_menu)


async def update_today_request_status_from_callback(
    callback: CallbackQuery,
    api_client: ApiClient,
    new_status: str,
) -> None:
    await _update_request_status_from_callback(
        callback, api_client, new_status, _render_today_request
    )


@router.callback_query(F.data == "admin_back_to_menu")
async def handle_back_to_admin_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=kb.admin_menu_keyboard(),
    )


@router.callback_query(F.data == "new_request")
async def handle_new_request(callback: CallbackQuery, api_client: ApiClient):
    is_success, error_text, request_data = await admin_service.get_first_new_request(
        api_client,
        callback.from_user.id,
    )

    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return

    if request_data is None:
        await callback.answer("Новых заявок нет.")
        return

    await callback.answer()
    await callback.message.edit_text(
        format_request_text(request_data),
        reply_markup=kb.admin_new_request_keyboard(request_data.id),
    )


@router.callback_query(F.data == "in_progress")
async def handle_in_progress_request(callback: CallbackQuery, api_client: ApiClient):
    is_success, error_text, request_data = await admin_service.get_first_in_progress_request(
        api_client,
        callback.from_user.id,
    )

    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return

    if request_data is None:
        await callback.answer("Заявок в работе нет.")
        return

    await callback.answer()
    await callback.message.edit_text(
        format_request_text(request_data),
        reply_markup=kb.admin_in_progress_request_keyboard(request_data.id),
    )


@router.callback_query(F.data == "today")
async def handle_today_request(callback: CallbackQuery, api_client: ApiClient):
    is_success, error_text, request_data = await admin_service.get_today_requests(
        api_client,
        callback.from_user.id,
    )

    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return

    if not request_data:
        await callback.answer("Заявок за сегодня нет")
        return

    today_request = request_data[0]
    reply_markup = get_today_request_keyboard(today_request)

    await callback.answer()
    await callback.message.edit_text(
        format_request_text(today_request),
        reply_markup=reply_markup,
    )


@router.message(Command("new_requests"))
async def handle_new_requests_command(message: Message, api_client: ApiClient):
    is_success, error_text, request_data = await admin_service.get_first_new_request(
        api_client,
        message.from_user.id,
    )
    if not is_success:
        await message.answer(error_text or "Сервис временно недоступен.")
        return

    await _send_first_admin_request(
        message,
        request_data,
        "Новых заявок нет.",
        kb.admin_new_request_keyboard,
    )


@router.message(Command("in_progress"))
async def handle_in_progress_command(message: Message, api_client: ApiClient):
    is_success, error_text, request_data = await admin_service.get_first_in_progress_request(
        api_client,
        message.from_user.id,
    )
    if not is_success:
        await message.answer(error_text or "Сервис временно недоступен.")
        return

    await _send_first_admin_request(
        message,
        request_data,
        "Заявок в работе нет.",
        kb.admin_in_progress_request_keyboard,
    )


@router.message(Command("today"))
async def handle_today_command(message: Message, api_client: ApiClient):
    is_success, error_text, requests = await admin_service.get_today_requests(
        api_client,
        message.from_user.id,
    )
    if not is_success:
        await message.answer(error_text or "Сервис временно недоступен.")
        return

    if not requests:
        await message.answer("Заявок за сегодня нет.")
        return

    request_data = requests[0]
    await message.answer(
        format_request_text(request_data),
        reply_markup=get_today_request_keyboard(request_data),
    )


@router.callback_query(F.data.startswith("view_request:"))
async def handle_view_request(callback: CallbackQuery, api_client: ApiClient):
    request_id = int(callback.data.split(":", maxsplit=1)[1])
    is_success, error_text, request_data = await admin_service.get_request_for_admin(
        api_client,
        callback.from_user.id,
        request_id,
    )

    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return

    reply_markup = None
    if request_data.status == StatusEnum.NEW.value:
        reply_markup = kb.admin_notification_request_keyboard(request_id)
    elif request_data.status == StatusEnum.IN_PROGRESS.value:
        reply_markup = kb.admin_in_progress_request_keyboard(request_id)

    await callback.answer()
    await callback.message.answer(
        format_request_text(request_data),
        reply_markup=reply_markup,
    )


@router.callback_query(F.data.startswith("next_new_request:"))
async def handle_next_new_request(callback: CallbackQuery, api_client: ApiClient):
    request_id = int(callback.data.split(":", maxsplit=1)[1])
    is_success, error_text, new_request = await get_adjacent_request(
        api_client,
        callback.from_user.id,
        request_id,
        direction=1,
        status_to_find=StatusEnum.NEW.value,
    )
    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return
    if new_request is None:
        await callback.answer(error_text, show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(
        format_request_text(new_request),
        reply_markup=kb.admin_new_request_keyboard(new_request.id),
    )


@router.callback_query(F.data.startswith("next_today_request:"))
async def handle_next_today_request(callback: CallbackQuery, api_client: ApiClient):
    request_id = int(callback.data.split(":", maxsplit=1)[1])
    is_success, error_text, today_request = await get_adjacent_today_request(
        api_client,
        callback.from_user.id,
        request_id,
        direction=1,
    )

    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        format_request_text(today_request),
        reply_markup=get_today_request_keyboard(today_request),
    )


@router.callback_query(F.data.startswith("previous_today_request:"))
async def handle_previous_today_request(callback: CallbackQuery, api_client: ApiClient):
    request_id = int(callback.data.split(":", maxsplit=1)[1])
    is_success, error_text, today_request = await get_adjacent_today_request(
        api_client,
        callback.from_user.id,
        request_id,
        direction=-1,
    )

    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        format_request_text(today_request),
        reply_markup=get_today_request_keyboard(today_request),
    )


@router.callback_query(F.data.startswith("next_in_progress:"))
async def handle_next_in_progress_request(callback: CallbackQuery, api_client: ApiClient):
    request_id = int(callback.data.split(":", maxsplit=1)[1])
    is_success, error_text, new_request = await get_adjacent_request(
        api_client,
        callback.from_user.id,
        request_id,
        direction=1,
        status_to_find=StatusEnum.IN_PROGRESS.value,
    )
    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return
    if new_request is None:
        await callback.answer(error_text, show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(
        format_request_text(new_request),
        reply_markup=kb.admin_in_progress_request_keyboard(new_request.id),
    )


@router.callback_query(F.data.startswith("previous_in_progress:"))
async def handle_previous_in_progress_request(callback: CallbackQuery, api_client: ApiClient):
    request_id = int(callback.data.split(":", maxsplit=1)[1])
    is_success, error_text, new_request = await get_adjacent_request(
        api_client,
        callback.from_user.id,
        request_id,
        direction=-1,
        status_to_find=StatusEnum.IN_PROGRESS.value,
    )
    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return
    if new_request is None:
        await callback.answer(error_text, show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(
        format_request_text(new_request),
        reply_markup=kb.admin_in_progress_request_keyboard(new_request.id),
    )


@router.callback_query(F.data.startswith("previous_new_request:"))
async def handle_previous_new_request(callback: CallbackQuery, api_client: ApiClient):
    request_id = int(callback.data.split(":", maxsplit=1)[1])
    is_success, error_text, new_request = await get_adjacent_request(
        api_client,
        callback.from_user.id,
        request_id,
        direction=-1,
        status_to_find=StatusEnum.NEW.value,
    )
    if not is_success:
        await callback.answer(error_text, show_alert=True)
        return
    if new_request is None:
        await callback.answer(error_text, show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(
        format_request_text(new_request),
        reply_markup=kb.admin_new_request_keyboard(new_request.id),
    )


@router.callback_query(F.data.startswith("take_request:"))
async def handle_take_request(callback: CallbackQuery, api_client: ApiClient):
    await update_new_request_status_from_callback(
        callback, api_client, StatusEnum.IN_PROGRESS.value
    )


@router.callback_query(F.data.startswith("complete_request:"))
async def handle_complete_request(callback: CallbackQuery, api_client: ApiClient):
    await update_in_progress_request_status_from_callback(
        callback, api_client, StatusEnum.COMPLETED.value
    )


@router.callback_query(F.data.startswith("reject_in_progress_request:"))
async def handle_reject_in_progress_request(callback: CallbackQuery, api_client: ApiClient):
    await update_in_progress_request_status_from_callback(
        callback, api_client, StatusEnum.REJECTED.value
    )


@router.callback_query(F.data.startswith("reject_new_request:"))
async def handle_reject_new_request(callback: CallbackQuery, api_client: ApiClient):
    await update_new_request_status_from_callback(callback, api_client, StatusEnum.REJECTED.value)


@router.callback_query(F.data.startswith("take_notification_request:"))
async def handle_take_notification_request(callback: CallbackQuery, api_client: ApiClient):
    await update_notification_request_status_from_callback(
        callback,
        api_client,
        StatusEnum.IN_PROGRESS.value,
    )


@router.callback_query(F.data.startswith("reject_notification_request:"))
async def handle_reject_notification_request(callback: CallbackQuery, api_client: ApiClient):
    await update_notification_request_status_from_callback(
        callback,
        api_client,
        StatusEnum.REJECTED.value,
    )


@router.callback_query(F.data.startswith("take_today_request:"))
async def handle_take_today_request(callback: CallbackQuery, api_client: ApiClient):
    await update_today_request_status_from_callback(
        callback,
        api_client,
        StatusEnum.IN_PROGRESS.value,
    )


@router.callback_query(F.data.startswith("reject_today_request:"))
async def handle_reject_today_request(callback: CallbackQuery, api_client: ApiClient):
    await update_today_request_status_from_callback(
        callback,
        api_client,
        StatusEnum.REJECTED.value,
    )


@router.callback_query(F.data.startswith("complete_today_request:"))
async def handle_complete_today_request(callback: CallbackQuery, api_client: ApiClient):
    await update_today_request_status_from_callback(
        callback,
        api_client,
        StatusEnum.COMPLETED.value,
    )


@router.callback_query(F.data.startswith("reject_today_in_progress_request:"))
async def handle_reject_today_in_progress_request(
    callback: CallbackQuery,
    api_client: ApiClient,
):
    await update_today_request_status_from_callback(
        callback,
        api_client,
        StatusEnum.REJECTED.value,
    )
