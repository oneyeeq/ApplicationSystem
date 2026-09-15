from datetime import datetime, timedelta, timezone
import logging

from app.database import session_factory
from app.services.request_service import delete_expired_closed_requests
from config import settings

logger = logging.getLogger(__name__)


async def cleanup_closed_requests() -> int:
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        days=settings.COMPLETED_REQUEST_RETENTION_DAYS
    )
    async with session_factory() as db:
        deleted_count = await delete_expired_closed_requests(db, cutoff)

    logger.info("Удалено закрытых заявок: %s", deleted_count)
    return deleted_count
