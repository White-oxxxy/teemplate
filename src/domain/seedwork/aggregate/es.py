from abc import (
    ABC,
    abstractmethod,
)
from copy import copy
from dataclasses import (
    dataclass,
    field,
)
from typing import TypeVar

from domain.seedwork.entity import Entity
from domain.seedwork.event import DomainEvent


ESAggregateType = TypeVar("ESAggregateType", bound="BaseESAggregate")


@dataclass(
    slots=True,
    kw_only=True,
)
class BaseESAggregate(
    Entity,
    ABC,
):
    _version: int = 0
    _uncommitted_events: list[DomainEvent] = field(default_factory=list)

    @property
    def get_version(self) -> int:
        return self._version

    @property
    def get_uncommited_events(self) -> list[DomainEvent]:
        uncommited_events: list[DomainEvent] = copy(self._uncommitted_events)

        return uncommited_events

    def mark_events_as_commited(self) -> None:
        self._uncommitted_events.clear()

    @abstractmethod
    def when(self, event: DomainEvent) -> None: ...

    def apply_event(
        self,
        event: DomainEvent,
        is_new: bool = True,
    ) -> None:
        self.when(event=event)
        self._version += 1

        if is_new:
            event.aggregate_version = self._version

            self._uncommitted_events.append(event)