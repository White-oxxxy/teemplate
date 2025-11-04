from abc import (
    ABC,
    abstractmethod,
)
from copy import copy
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Any,
    TypeVar,
)

from domain.seedwork.value_objects.value import EntityIdValue
from domain.seedwork.entity import Entity
from domain.seedwork.event import DomainEvent
from domain.seedwork.aggregate.es.snapshot import AggregateSnapshot
from domain.seedwork.aggregate.es.exceptions import (
    CannotRecoverAggregateFromEmptyEventHistoryException,
    FirstEventDontIncludeAggregateIdException,
)


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

    @classmethod
    def from_history(
        cls: type[ESAggregateType],
        events: list[DomainEvent],
    ) -> ESAggregateType:
        if len(events) == 0:
            raise CannotRecoverAggregateFromEmptyEventHistoryException()

        aggregate_id: EntityIdValue | None = getattr(events[0], "aggregate_id", None)

        if aggregate_id is None:
            raise FirstEventDontIncludeAggregateIdException()

        aggregate: ESAggregateType = cls(aggregate_id)

        for event in events:
            aggregate.apply_event(event, is_new=False)

        return aggregate

    @abstractmethod
    def get_snapshot_data(self) -> Any: ...

    @abstractmethod
    def apply_snapshot_data(self, data: Any) -> None: ...

    @classmethod
    def from_snapshot(
        cls: type[ESAggregateType],
        snapshot: AggregateSnapshot,
    ) -> ESAggregateType:
        aggregate: ESAggregateType = cls(snapshot.aggregate_id)

        aggregate._version = snapshot.version

        aggregate.apply_snapshot_data(snapshot.data)

        return aggregate
