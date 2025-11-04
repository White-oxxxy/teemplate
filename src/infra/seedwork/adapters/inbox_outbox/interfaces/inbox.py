from dataclasses import dataclass
from typing import Protocol

from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.message import InboxMessage


@dataclass
class Inbox(Protocol):
    async def add(self, event: DomainEvent) -> None: ...

    async def get_next_pending(self) -> InboxMessage | None: ...

    async def mark_as_processed(self) -> None: ...

    async def mark_as_failed(self) -> None: ...

    async def to_processed(self) -> list[InboxMessage]: ...