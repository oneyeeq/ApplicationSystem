import fcntl
import os
from pathlib import Path

import aiohttp
from aiogram import Bot, Dispatcher

from bot.clients.api_client import ApiClient
from bot.handlers.admin_handler import router as admin_router
from bot.handlers.request_handler import router as request_router
from bot.handlers.start_handler import router as start_router
from bot.middlewares.admin_auth import AdminAuthMiddleware
from config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

admin_router.message.middleware(AdminAuthMiddleware())
admin_router.callback_query.middleware(AdminAuthMiddleware())

dp.include_router(start_router)
dp.include_router(request_router)
dp.include_router(admin_router)


def acquire_instance_lock():
    lock_path = Path(__file__).resolve().parent.parent / ".bot.lock"
    lock_file = lock_path.open("a+")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        lock_file.seek(0)
        owner_pid = lock_file.read().strip() or "неизвестен"
        lock_file.close()
        raise RuntimeError(f"Бот уже запущен в другом процессе (PID: {owner_pid})") from error
    lock_file.seek(0)
    lock_file.truncate()
    lock_file.write(str(os.getpid()))
    lock_file.flush()
    return lock_file


async def main():
    lock_file = acquire_instance_lock()
    timeout = aiohttp.ClientTimeout(total=settings.API_REQUEST_TIMEOUT)
    try:
        async with aiohttp.ClientSession(
            timeout=timeout,
            headers={"X-Service-Token": settings.SERVICE_TOKEN},
        ) as session:
            api_client = ApiClient(session)
            dp["api_client"] = api_client
            await dp.start_polling(bot)
    finally:
        lock_file.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
