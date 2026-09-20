from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

START_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Оставить заявку",
                callback_data="request",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Мои заявки",
                callback_data="my_requests",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Помощь",
                callback_data="help",
            ),
        ],
    ]
)

SERVICES_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сайт")],
        [KeyboardButton(text="Бот")],
        [KeyboardButton(text="Скрипт")],
        [KeyboardButton(text="Отменить заявку")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отменить заявку")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

PHONE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Поделиться телефоном",
                request_contact=True,
            )
        ],
        [KeyboardButton(text="Отменить заявку")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

BACK_TO_MENU_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Вернуться в меню",
                callback_data="back_to_menu",
            )
        ]
    ]
)

SUBMIT_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Отправить заявку",
                callback_data="submit",
            )
        ],
        [
            InlineKeyboardButton(
                text="Отменить заявку",
                callback_data="cancelrequest",
            )
        ],
    ]
)
