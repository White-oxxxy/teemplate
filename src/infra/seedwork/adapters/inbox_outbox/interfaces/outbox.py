from dataclasses import dataclass
from typing import Protocol

from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.message import OutboxMessage


@dataclass
class Outbox(Protocol):
    async def add(self, event: DomainEvent) -> None: ...

    async def get_next_pending(self) -> OutboxMessage | None: ...

    async def mark_as_published(self, message: OutboxMessage) -> None: ...

    async def mark_as_failed(self, message: OutboxMessage) -> None: ...

    async def to_publish(self) -> list[OutboxMessage]: ...