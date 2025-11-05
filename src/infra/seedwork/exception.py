from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass(eq=False)
class InfraException(
    Exception,
    ABC,
):
    @abstractmethod
    @property
    def message(self) -> str:
        message = f"Infra exception!"

        return message