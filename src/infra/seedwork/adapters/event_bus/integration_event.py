from abc import ABC
from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from msgspec import (
    Struct,
    field,
)
from uuid_utils import uuid7


class BaseIntegrationEvent(
    Struct,
    frozen=True,
    kw_only=True,
    ABC,
):
    event_id: UUID = field(default_factory=uuid7)
    event_type: str
    aggregate_id: str
    aggregate_type: str
    aggregate_version: int | None = None
    accurate_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_context: str