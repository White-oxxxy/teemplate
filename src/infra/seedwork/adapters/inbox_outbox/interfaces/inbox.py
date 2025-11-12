from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent


@dataclass
class Inbox(Protocol):
    async def add(self, event: BaseIntegrationEvent) -> None: ...

    async def get_next_pending(self) -> BaseIntegrationEvent | None: ...

    async def mark_as_processed(self, event_id: UUID) -> None: ...

    async def mark_as_failed(self, event_id: UUID) -> None: ...

    async def to_processed(self) -> list[BaseIntegrationEvent]: ...