from dataclasses import dataclass

from sqlalchemy import (
    Result,
    Select,
    Update,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.message import (
    OutboxMessage,
    MessageStatus,
)
from infra.seedwork.adapters.inbox_outbox.exceptions.outbox import (
    OutboxMessageAlreadyExistException,
    CannotMarkPublishedAlreadyPublishedMessageException,
    OutboxMessageNotFoundException,
)
from infra.seedwork.adapters.inbox_outbox.convertors.outbox import convert_domain_event_to_outbox_message
from infra.seedwork.db.models.outbox import OutboxMessageModel
from infra.seedwork.db.convertors.outbox import (
    convert_outbox_message_to_model,
    convert_outbox_model_to_message,
)


@dataclass
class SQLAlchemyOutboxImpl:
    _session: AsyncSession

    async def add(self, event: DomainEvent) -> None:
        message: OutboxMessage = convert_domain_event_to_outbox_message(event=event)

        message_orm: OutboxMessageModel = convert_outbox_message_to_model(message,)

        self._session.add(message_orm)

        try:
            await self._session.flush()

        except IntegrityError as err:

            raise OutboxMessageAlreadyExistException(message_id=message.id) from err

    async def get_next_pending(self) -> OutboxMessage | None:
        stmt: Select[tuple["OutboxMessageModel"]] = (
            select(OutboxMessageModel)
            .where(OutboxMessageModel.status == MessageStatus.PENDING)
            .order_by(OutboxMessageModel.event_created_at.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )

        result: Result[tuple["OutboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orm: OutboxMessageModel | None = result.scalar_one_or_none()

        if message_orm is None:

            return None

        message_orm.status = MessageStatus.PROCESSING

        await self._session.flush()

        message: OutboxMessage = convert_outbox_model_to_message(message_orm,)

        return message

    async def mark_as_published(self, message: OutboxMessage) -> None:
        stmt: Update = (
            update(OutboxMessageModel)
            .where(
                OutboxMessageModel.id == message.id,
                OutboxMessageModel.status != MessageStatus.PUBLISHED
            )
            .values(status=MessageStatus.PUBLISHED)
            .execution_options(synchronize_session="fetch")
            .returning(OutboxMessageModel.status)
        )

        result: Result = await self._session.execute(stmt)

        status_row = result.first()

        await self._session.flush()

    async def mark_as_failed(self, message: OutboxMessage) -> None: ...

    async def to_publish(self) -> list[OutboxMessage]: ...