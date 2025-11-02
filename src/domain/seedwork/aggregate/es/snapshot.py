from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)
from typing import Any

from domain.seedwork.value_objects.value import EntityIdValue


@dataclass(slots=True)
class AggregateSnapshot:
    aggregate_id: EntityIdValue
    aggregate_type: str
    version: int
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
