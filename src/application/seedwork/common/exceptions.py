from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationError(
    Exception,
    ABC,
):
    @abstractmethod
    @property
    def message(self) -> str:
        message = f"Application error!"

        return message


@dataclass(eq=False)
class MappingError(ApplicationError):
    @property
    def message(self) -> str:
        message = f"Mapping error!"

        return message