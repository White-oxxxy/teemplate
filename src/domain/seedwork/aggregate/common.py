from abc import ABC
from copy import copy
from dataclasses import (
    dataclass,
    field,
)

from domain.seedwork.entity import TimestampEntity
from domain.seedwork.event import DomainEvent


@dataclass(
    kw_only=True,
    slots=True,
)
class BaseAggregate(
    TimestampEntity,
    ABC,
):
    _events: list[DomainEvent] = field(default_factory=list)

    def register_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        registered_events = copy(self._events)

        self._events.clear()

        return registered_events