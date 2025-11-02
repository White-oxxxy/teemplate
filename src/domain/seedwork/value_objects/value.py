from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    TypeVar,
)

from domain.seedwork.value_objects.exception import EmptyValueException


@dataclass(
    frozen=True,
    slots=True,
)
class BaseValueObject(ABC):
    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self) -> None: ...


ValueType = TypeVar("ValueType", bound=Any)


@dataclass(
    frozen=True,
    slots=True,
)
class BaseSimpleValueObject(
    BaseValueObject,
    Generic[ValueType],
    ABC,
):
    _value: ValueType

    def validate(self) -> None:
        if self._value is None:
            raise EmptyValueException()

    @property
    def get_value(self) -> ValueType:
        return self._value

    def __eq__(self, __value: "BaseSimpleValueObject") -> bool:
        if not isinstance(__value, BaseSimpleValueObject):
            raise NotImplemented

        return self._value == __value


@dataclass(
    frozen=True,
    slots=True,
)
class EntityIdValue(BaseSimpleValueObject[Any]):
    def validate(self) -> None:
        super().validate()


@dataclass(
    frozen=True,
    slots=True,
)
class BaseCompositeValueObject(
    BaseValueObject,
    ABC,
):
    ...