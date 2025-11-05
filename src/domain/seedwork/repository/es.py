from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Generic

from domain.seedwork.value_objects.value import EntityIdValue
from domain.seedwork.aggregate.es import ESAggregateType


@dataclass
class BaseESRepository(
    Generic[ESAggregateType],
    ABC,
):
    @abstractmethod
    async def find_by_id(self, required_id: EntityIdValue) -> ESAggregateType | None: ...

    @abstractmethod
    async def save(self, aggregate: ESAggregateType) -> None: ...

    @abstractmethod
    async def get_version(self, aggregate_id: EntityIdValue) -> int: ...

    @abstractmethod
    async def exist(self, required_id: EntityIdValue) -> bool: ...