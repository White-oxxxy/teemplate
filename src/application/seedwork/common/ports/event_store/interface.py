from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from application.seedwork.common.ports.event_store.stored_event import StoredEvent
from domain.seedwork.value_objects.value import EntityIdValue
from domain.seedwork.event import DomainEvent


@dataclass
class EventStore(Protocol):
    async def save_events(
        self,
        aggregate_id: EntityIdValue,
        events: list[DomainEvent],
        expected_version: int,
    ) -> None: ...

    async def get_events_for_aggregate(
        self,
        aggregate_id: EntityIdValue,
        from_version: int,
    ) -> list[StoredEvent]: ...

    async def get_events_by_aggregate_type(
        self,
        aggregate_type: str,
        from_date: datetime,
        to_date: datetime,
    ) -> list[StoredEvent]: ...

    async def get_events_after(self, date: datetime) -> list[StoredEvent]: ...