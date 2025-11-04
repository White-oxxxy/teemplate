from dataclasses import dataclass
from typing import Protocol

from domain.seedwork.aggregate.es.snapshot import AggregateSnapshot
from domain.seedwork.value_objects.value import EntityIdValue


@dataclass
class SnapshotStore(Protocol):
    async def save_snapshot(self, snapshot: AggregateSnapshot) -> None: ...

    async def get_snapshot(self, aggregate_id: EntityIdValue) -> AggregateSnapshot | None: ...

    async def cleanup_snapshots(
        self,
        aggregate_id: EntityIdValue,
        count: int = 1,
    ) -> None: ...