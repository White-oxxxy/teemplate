from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from domain.seedwork.exception import DomainException


@dataclass(eq=False)
class ESAggregateException(
    DomainException,
    ABC,
):
    @property
    @abstractmethod
    def message(self) -> str:
        message = f"Es aggregate exception"

        return message


@dataclass(eq=False)
class CannotRecoverAggregateFromEmptyEventHistoryException(ESAggregateException):
    @property
    def message(self) -> str:
        message = f"Cannot recover aggregate from empty event history!"

        return message


@dataclass(eq=False)
class FirstEventDontIncludeAggregateIdException(ESAggregateException):
    @property
    def message(self) -> str:
        message = f"First event dont include aggregate id"

        return message