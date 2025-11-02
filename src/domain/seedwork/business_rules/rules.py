from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class BaseBusinessRule(ABC):
    @abstractmethod
    def is_broken(self) -> bool: ...

    @abstractmethod
    def get_message(self) -> str: ...