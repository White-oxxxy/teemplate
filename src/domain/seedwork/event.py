from abc import ABC
from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)

from domain.seedwork.value_objects.value import EntityIdValue


@dataclass(
    slots=True,
    kw_only=True,
)
class DomainEvent(ABC):
    event_id: str
    event_version: int = 1
    aggregate_id: EntityIdValue
    aggregate_type: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))