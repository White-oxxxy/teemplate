from abc import ABC
from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)

from domain.seedwork.value_objects.value import EntityIdValue


@dataclass(
    kw_only=True,
    slots=True,
)
class Entity(ABC):
    _id: EntityIdValue = field(repr=False)

    @property
    def get_id(self) -> EntityIdValue:
        return self._id

    def __hash__(self) -> int:
        return hash(self._id.get_value)

    def __eq__(self, __other: "Entity") -> bool:
        if not isinstance(__other, Entity):
            raise NotImplemented

        return self._id == __other._id


@dataclass(
    kw_only=True,
    slots=True,
)
class TimestampEntity(
    Entity,
    ABC,
):
    _created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def get_created_time(self) -> datetime:
        return self._created_at

    @property
    def get_updated_time(self) -> datetime:
        return self._updated_at

    def _touch(self) -> None:
        self._updated_at = datetime.now(tz=timezone.utc)