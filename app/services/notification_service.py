import logging

from aiogram import Bot
from aiogram.exceptions import AiogramError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.exc import SQLAlchemyError

from app.services import admin_service
from app.models.user_model import User
from app.database import session_factory
from app.services.exceptions import AdminNotFoundError
from config import settings
from enums import StatusEnum

logger = logging.getLogger(__name__)


async def notify_admins_about_request(request_id: int) -> None:
    admins = await _get_active_admins()
    if not admins:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Посмотреть заявку",
                    callback_data=f"view_request:{request_id}",
                )
            ]
        ]
    )

    bot = Bot(token=settings.BOT_TOKEN)
    try:
        for admin in admins:
            try:
                await bot.send_message(
                    chat_id=admin.tg_admin_id,
                    text="Новая заявка",
                    reply_markup=keyboard,
                )
            except AiogramError:
                logger.exception(
                    "Не удалось уведомить администратора %s о заявке %s",
                    admin.tg_admin_id,
                    request_id,
                )
    finally:
        await bot.session.close()


async def notify_user_about_status(request) -> None:
    async with session_factory() as db:
        user = await db.get(User, request.user_id)

    if user is None or not user.is_active:
        return

    status_text = {
        StatusEnum.IN_PROGRESS.value: "Заявка принята и взята в работу.",
        StatusEnum.COMPLETED.value: "Заявка завершена.",
        StatusEnum.REJECTED.value: "Заявка отклонена.",
    }.get(request.status.value, "Статус заявки изменён.")

    bot = Bot(token=settings.BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=user.tg_user_id,
            text=f"Заявка №{request.id}\n{status_text}",
        )
    except AiogramError:
        logger.exception("Не удалось уведомить пользователя о заявке %s", request.id)
    finally:
        await bot.session.close()


async def _get_active_admins():
    async with session_factory() as db:
        try:
            return await admin_service.get_active_admins(db)
        except AdminNotFoundError:
            return []
        except SQLAlchemyError:
            logger.exception("Не удалось получить список активных администраторов")
            return []