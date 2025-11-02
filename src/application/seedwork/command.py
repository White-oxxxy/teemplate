from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Generic,
    TypeVar,
)


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class BaseCommand(ABC): ...


CommandType = TypeVar("CommandType", bound=BaseCommand)


@dataclass
class BaseCommandHandler(
    Generic[CommandType],
    ABC,
):
    @abstractmethod
    async def handle(self, command: CommandType) -> None: ...