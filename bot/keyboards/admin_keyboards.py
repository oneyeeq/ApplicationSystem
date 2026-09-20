from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def request_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Посмотреть заявку",
                    callback_data=f"view_request:{request_id}",
                )
            ]
        ]
    )


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Новые заявки",
                    callback_data="new_request",
                )
            ],
            [
                InlineKeyboardButton(
                    text="В работе",
                    callback_data="in_progress",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Сегодня",
                    callback_data="today",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Помощь",
                    callback_data="help",
                )
            ],
        ]
    )


def _action_row(
    primary_text: str,
    primary_callback: str,
    secondary_text: str,
    secondary_callback: str,
) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text=primary_text, callback_data=primary_callback),
        InlineKeyboardButton(text=secondary_text, callback_data=secondary_callback),
    ]


def _nav_row(previous_callback: str, next_callback: str) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text="Предыдущая", callback_data=previous_callback),
        InlineKeyboardButton(text="Следующая", callback_data=next_callback),
    ]


def _with_back_to_menu(
    keyboard: list[list[InlineKeyboardButton]],
    include_back_to_menu: bool,
) -> InlineKeyboardMarkup:
    if include_back_to_menu:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Вернуться в меню",
                    callback_data="admin_back_to_menu",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_notification_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        _action_row(
            "Принять",
            f"take_notification_request:{request_id}",
            "Отклонить",
            f"reject_notification_request:{request_id}",
        ),
    ]
    return _with_back_to_menu(keyboard, include_back_to_menu)


def admin_new_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        _action_row(
            "Принять",
            f"take_request:{request_id}",
            "Отклонить",
            f"reject_new_request:{request_id}",
        ),
        _nav_row(f"previous_new_request:{request_id}", f"next_new_request:{request_id}"),
    ]
    return _with_back_to_menu(keyboard, include_back_to_menu)


def admin_in_progress_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        _action_row(
            "Завершить",
            f"complete_request:{request_id}",
            "Отклонить",
            f"reject_in_progress_request:{request_id}",
        ),
        _nav_row(f"previous_in_progress:{request_id}", f"next_in_progress:{request_id}"),
    ]
    return _with_back_to_menu(keyboard, include_back_to_menu)


def admin_today_in_progress_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        _action_row(
            "Завершить",
            f"complete_today_request:{request_id}",
            "Отклонить",
            f"reject_today_request:{request_id}",
        ),
        _nav_row(f"previous_today_request:{request_id}", f"next_today_request:{request_id}"),
    ]
    return _with_back_to_menu(keyboard, include_back_to_menu)


def admin_today_new_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        _action_row(
            "Принять",
            f"take_today_request:{request_id}",
            "Отклонить",
            f"reject_today_request:{request_id}",
        ),
        _nav_row(f"previous_today_request:{request_id}", f"next_today_request:{request_id}"),
    ]
    return _with_back_to_menu(keyboard, include_back_to_menu)


def admin_today_closed_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        _nav_row(f"previous_today_request:{request_id}", f"next_today_request:{request_id}"),
    ]
    return _with_back_to_menu(keyboard, include_back_to_menu)
