from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass(eq=False)
class DomainException(
    Exception,
    ABC,
):
    @property
    @abstractmethod
    def message(self) -> str:
        message = f"Domain exception"

        return message