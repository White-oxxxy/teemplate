from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from domain.seedwork.value_objects.value import EntityIdValue


@dataclass
class IIdGenerator(ABC):
    @abstractmethod
    def generate_id(self) -> str: ...