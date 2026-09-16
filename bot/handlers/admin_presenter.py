from aiogram.types import InlineKeyboardMarkup

from enums import StatusEnum
import bot.keyboards.admin_keyboards as keyboards
from bot.dtos import RequestData


def format_request_text(request_data: RequestData) -> str:
    return (
        f"Заявка №{request_data.id}\n"
        f"Услуга: {request_data.service_name}\n"
        f"Телефон: {request_data.phone_number}\n"
        f"Статус: {request_data.status}"
    )


def get_today_request_keyboard(
    request_data: RequestData,
) -> InlineKeyboardMarkup | None:
    request_id = request_data.id
    status = request_data.status

    if status == StatusEnum.NEW.value:
        return keyboards.admin_today_new_request_keyboard(request_id)
    if status == StatusEnum.IN_PROGRESS.value:
        return keyboards.admin_today_in_progress_request_keyboard(request_id)
    if status in {StatusEnum.COMPLETED.value, StatusEnum.REJECTED.value}:
        return keyboards.admin_today_closed_request_keyboard(request_id)

    return None