from dataclasses import dataclass
from typing import Any

from application.seedwork.common.ports.event_store.event_metadata import EventMetadata


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class StoredEvent:
    event_metadata: EventMetadata
    serializable_data: dict[str, Any]