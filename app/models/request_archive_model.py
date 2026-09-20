from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from enums import StatusEnum


class ArchivedRequest(Base):
    __tablename__ = "archived_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Deliberately not a ForeignKey — an archived row is a historical record,
    # not a live relation. Keeping a FK here would block deleting a user
    # once their requests are archived, defeating the whole point of moving
    # them out of the active (ondelete=RESTRICT) request table.
    original_request_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[StatusEnum] = mapped_column(
        SAEnum(StatusEnum, native_enum=False),
        nullable=False,
    )

    # Copied as-is from the original request — when it was created/last
    # touched, not when it was archived.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
