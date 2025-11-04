from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)
from enum import StrEnum
from typing import Any
from uuid import UUID

from uuid_utils import uuid7


class MessageStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PUBLISHED = "PUBLISHED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class OutboxMessage:
    id: UUID = field(default_factory=uuid7)
    event_id: UUID
    event_type: str
    aggregate_id: str
    aggregate_type: str
    aggregate_version: int | None = None
    payload: dict[str, Any]
    source_context: str
    status: MessageStatus = field(default=MessageStatus.PENDING)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: datetime | None = None


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class InboxMessage:
    id: UUID = field(default_factory=uuid7)
    event_id: UUID
    event_type: str
    aggregate_id: str
    aggregate_type: str
    aggregate_version: int | None = None
    payload: dict[str, Any]
    source_context: str
    status: MessageStatus = field(default=MessageStatus.PENDING)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: datetime | None = None
