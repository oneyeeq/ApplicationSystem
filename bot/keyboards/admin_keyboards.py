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


def admin_notification_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Принять",
                callback_data=f"take_notification_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=f"reject_notification_request:{request_id}",
            ),
        ]
    ]

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


def admin_new_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Принять",
                callback_data=f"take_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=f"reject_new_request:{request_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Предыдущая",
                callback_data=f"previous_new_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Следующая",
                callback_data=f"next_new_request:{request_id}",
            ),
        ],
    ]

    if include_back_to_menu:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Вернуться в меню",
                    callback_data="admin_back_to_menu",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )


def admin_in_progress_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Завершить",
                callback_data=f"complete_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=f"reject_in_progress_request:{request_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Предыдущая",
                callback_data=f"previous_in_progress:{request_id}",
            ),
            InlineKeyboardButton(
                text="Следующая",
                callback_data=f"next_in_progress:{request_id}",
            ),
        ],
    ]

    if include_back_to_menu:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Вернуться в меню",
                    callback_data="admin_back_to_menu",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )

def admin_today_in_progress_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Завершить",
                    callback_data=f"complete_today_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=f"reject_today_in_progress_request:{request_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Предыдущая",
                    callback_data=f"previous_today_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Следующая",
                    callback_data=f"next_today_request:{request_id}",
            ),
        ],
    ]

    if include_back_to_menu:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Вернуться в меню",
                    callback_data="admin_back_to_menu",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )


def admin_today_new_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Принять",
                callback_data=f"take_today_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=f"reject_today_request:{request_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Предыдущая",
                callback_data=f"previous_today_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Следующая",
                callback_data=f"next_today_request:{request_id}",
            ),
        ],
    ]

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


def admin_today_closed_request_keyboard(
    request_id: int,
    include_back_to_menu: bool = True,
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Предыдущая",
                callback_data=f"previous_today_request:{request_id}",
            ),
            InlineKeyboardButton(
                text="Следующая",
                callback_data=f"next_today_request:{request_id}",
            ),
        ]
    ]

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
