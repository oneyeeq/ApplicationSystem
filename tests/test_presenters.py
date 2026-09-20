from bot.dtos import RequestData
from bot.handlers.admin_presenter import (
    format_request_text,
    get_today_request_keyboard,
)
from bot.presenters.user_requests import format_user_requests


def make_request(request_id: int, status: str, service_name: str = "Сайт") -> RequestData:
    return RequestData(
        id=request_id,
        service_name=service_name,
        phone_number="+100",
        user_id=1,
        status=status,
        created_at="2026-09-14T00:00:00Z",
        updated_at="2026-09-14T00:00:00Z",
    )


def test_admin_presenter_formats_request():
    result = format_request_text(make_request(1, "новая"))

    assert "Заявка №1" in result
    assert "Услуга: Сайт" in result
    assert "Статус: новая" in result


def test_admin_presenter_uses_status_specific_keyboard():
    keyboard = get_today_request_keyboard(make_request(7, "новая"))

    assert keyboard is not None
    assert keyboard.inline_keyboard[0][0].callback_data == "take_today_request:7"


def test_user_presenter_formats_multiple_requests():
    result = format_user_requests(
        [
            make_request(1, "новая"),
            make_request(2, "завершена", "Бот"),
        ]
    )

    assert "Заявка №1" in result
    assert "Заявка №2" in result
    assert "\n\n" in result
