from datetime import (
    datetime,
    timezone,
)
from typing import Any
from uuid import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.sql.sqltypes import (
    DateTime,
    Enum,
    JSON,
)
from uuid_utils import uuid7

from infra.seedwork.db.models.base import TimedBaseModel
from infra.seedwork.adapters.inbox_outbox.message import MessageStatus


class InboxMessageModel(TimedBaseModel):
    __tablename__ = "inbox"

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid7)
    event_id: Mapped[UUID] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(nullable=False)
    aggregate_id: Mapped[str] = mapped_column(nullable=False)
    aggregate_type: Mapped[str] = mapped_column(nullable=False)
    aggregate_version: Mapped[int | None] = mapped_column(nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    source_context: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus, name="inbox_message_status"),
        default=MessageStatus.PENDING,
        nullable=False,
    )
    event_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )