from dataclasses import dataclass
from datetime import datetime
from typing import Any

from domain.seedwork.value_objects.value import EntityIdValue


@dataclass(
    slots=True,
    frozen=True,
    kw_only=True,
)
class EventMetadata:
    event_id: str
    event_type: str
    event_version: int
    aggregate_id: EntityIdValue
    aggregate_type: str
    aggregate_version: int
    timestamp: datetime
    extended_metadata: dict[str, Any]


