from dataclasses import dataclass
from typing import Protocol


@dataclass
class TransactionalManager(Protocol):
    async def commit(self) -> None: ...

    async def flush(self) -> None: ...