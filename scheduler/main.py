import asyncio
import logging

from config import settings
from scheduler.jobs.cleanup import archive_stale_requests_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def run() -> None:
    while True:
        await archive_stale_requests_job()
        await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Планировщик остановлен")
