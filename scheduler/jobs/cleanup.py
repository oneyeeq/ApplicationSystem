import logging
from datetime import datetime, timedelta, timezone

from app.database import session_factory
from app.services.request_service import archive_stale_requests
from config import settings

logger = logging.getLogger(__name__)


async def archive_stale_requests_job() -> int:
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        days=settings.REQUEST_STALE_DAYS
    )
    async with session_factory() as db:
        archived_count = await archive_stale_requests(db, cutoff)

    logger.info("Заархивировано заявок: %s", archived_count)
    return archived_count
