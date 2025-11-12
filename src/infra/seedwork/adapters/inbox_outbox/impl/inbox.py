from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import (
    Result,
    Select,
    Update,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent
from infra.seedwork.adapters.inbox_outbox.message import (
    InboxMessage,
    MessageStatus,
)
from infra.seedwork.db.models.inbox import InboxMessageModel
from infra.seedwork.db.convertors.inbox import InboxMessageModelConvertor
from infra.seedwork.adapters.inbox_outbox.convertors.inbox import (
    IntegrationEventToInboxMessageConvertor,
    InboxMessageToIntegrationEvnetConvertor,
)


@dataclass
class SQLAlchemyInboxImpl:
    _session: AsyncSession
    _model_message_convertor: InboxMessageModelConvertor
    _integration_event_to_message_convertor: IntegrationEventToInboxMessageConvertor
    _message_to_integration_event_convertor: InboxMessageToIntegrationEvnetConvertor

    async def add(self, event: BaseIntegrationEvent) -> None: ...

    async def get_next_pending(self) -> BaseIntegrationEvent | None: ...

    async def mark_as_processed(self, event_id: UUID) -> None: ...

    async def mark_as_failed(self, event_id: UUID) -> None: ...

    async def to_processed(self) -> list[BaseIntegrationEvent]: ...