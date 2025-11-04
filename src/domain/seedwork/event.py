from abc import ABC
from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from uuid_utils import uuid7

from domain.seedwork.value_objects.value import EntityIdValue


@dataclass(
    slots=True,
    kw_only=True,
)
class DomainEvent(ABC):
    event_id: UUID = field(default_factory=uuid7)
    event_version: int = 1
    aggregate_id: EntityIdValue
    aggregate_type: str
    aggregate_version: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))