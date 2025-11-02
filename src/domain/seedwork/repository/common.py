from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Generic,
    TypeVar,
)

from domain.seedwork.value_objects.value import EntityIdValue
from domain.seedwork.entity import Entity


EntityType = TypeVar("EntityType", bound=Entity)


@dataclass
class BaseRepository(
    Generic[EntityType],
    ABC,
):
    @abstractmethod
    async def find_by_id(self, required_id: EntityIdValue) -> EntityType | None: ...

    @abstractmethod
    async def find_all(self) -> list[EntityType]: ...

    @abstractmethod
    async def save(self, entity: EntityType) -> None: ...

    @abstractmethod
    async def update(self, entity: EntityType) -> None: ...

    @abstractmethod
    async def delete(self, entity_id: EntityIdValue) -> None: ...

    @abstractmethod
    async def exist(self, entity_id: EntityIdValue) -> bool: ...