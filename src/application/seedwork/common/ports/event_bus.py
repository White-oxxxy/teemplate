from dataclasses import dataclass
from typing import Protocol

from domain.seedwork.event import DomainEvent


@dataclass
class EventBus(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...