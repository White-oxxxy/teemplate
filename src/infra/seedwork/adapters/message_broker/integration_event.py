from abc import ABC
from dataclasses import dataclass, field
from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from uuid_utils import uuid7


@dataclass(
    frozen=True,
    kw_only=True,
    slots=True,
)
class BaseIntegrationEvent(ABC):
    event_id: UUID = field(default_factory=uuid7)
    event_type: str
    aggregate_id: str
    aggregate_type: str
    aggregate_version: int | None = None
    accurate_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_context: str