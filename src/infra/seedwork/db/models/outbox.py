from datetime import (
    datetime,
    timezone,
)
from typing import Any
from uuid import UUID

from sqlalchemy import Index
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


class OutboxMessageModel(TimedBaseModel):
    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default_factory=uuid7,
    )
    event_id: Mapped[UUID] = mapped_column(
        unique=True,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(nullable=False)
    aggregate_id: Mapped[str] = mapped_column(nullable=False)
    aggregate_type: Mapped[str] = mapped_column(nullable=False)
    aggregate_version: Mapped[int | None] = mapped_column(nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    source_context: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus, name="outbox_message_status"),
        default=MessageStatus.PENDING,
        nullable=False,
    )
    event_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_outbox_event_id_processing",
            "event_id",
            postgresql_where=(status == MessageStatus.PROCESSING)
        ),
    )