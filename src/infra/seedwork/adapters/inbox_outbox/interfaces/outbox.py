from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent


@dataclass
class Outbox(Protocol):
    async def add(self, event: DomainEvent) -> None: ...

    async def get_next_pending(self) -> BaseIntegrationEvent | None: ...

    async def mark_as_published(self, event_id: UUID) -> None: ...

    async def mark_as_failed(self, event_id: UUID) -> None: ...

    async def to_publish(self) -> list[BaseIntegrationEvent]: ...