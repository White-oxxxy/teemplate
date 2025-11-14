from dataclasses import dataclass
import logging
from uuid import UUID

from sqlalchemy import (
    Result,
    Select,
    Update,
    select,
    update,
)
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.message import (
    OutboxMessage,
    MessageStatus,
)
from infra.seedwork.adapters.inbox_outbox.exceptions.outbox import (
    OutboxMessageAlreadyExistException,
    OutboxMessageNotFoundException,
)
from infra.seedwork.adapters.inbox_outbox.convertors.outbox import (
    DomainEventOutboxMessageConvertor,
    OutboxMessageIntegrationEventConvertor,
)
from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent
from infra.seedwork.db.models.outbox import OutboxMessageModel
from infra.seedwork.db.convertors.outbox import OutboxMessageModelConvertor


logger = logging.getLogger(__name__)


@dataclass
class SQLAlchemyOutboxImpl:
    _session: AsyncSession
    _model_message_convertor: OutboxMessageModelConvertor
    _domain_event_message_convertor: DomainEventOutboxMessageConvertor
    _message_integration_event_convertor: OutboxMessageIntegrationEventConvertor

    async def add(self, event: DomainEvent) -> None:
        message: OutboxMessage = self._domain_event_message_convertor.to_message(event=event)

        message_orm: OutboxMessageModel = self._model_message_convertor.to_orm(message=message)

        self._session.add(message_orm)

        try:
            await self._session.flush()

        except IntegrityError as err:
            logger.error(
                "Outbox: integrity error while adding message (event_id=%s): %s",
                event.event_id,
                exc_info=err,
            )

            raise OutboxMessageAlreadyExistException(event_id=event.event_id) from err

    async def get_next_pending(self) -> BaseIntegrationEvent | None:
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
            logger.debug("Outbox: no pending messages")

            return None

        logger.info("Outbox: picked pending message event_id=%s", message_orm.event_id)

        message_orm.status = MessageStatus.PROCESSING

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                "Outbox: flush error while changing status to PROCESSING! (event_id=%s)",
                message_orm.event_id,
                exc_info=err
            )

            raise err

        message: OutboxMessage = self._model_message_convertor.from_orm(model=message_orm)

        event: BaseIntegrationEvent = self._message_integration_event_convertor.to_event(
            message=message
        )

        return event

    async def mark_as_published(self, event_id: UUID) -> None:
        stmt: Update = (
            update(OutboxMessageModel)
            .where(
                OutboxMessageModel.event_id == event_id,
                OutboxMessageModel.status != MessageStatus.PUBLISHED,
                OutboxMessageModel.status == MessageStatus.PROCESSING,
            )
            .values(status=MessageStatus.PUBLISHED)
            .execution_options(synchronize_session="fetch")
            .returning(OutboxMessageModel)
        )

        result: Result[tuple["OutboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orm: OutboxMessageModel | None = result.scalar_one_or_none()

        if message_orm is None:
            logger.warning("Outbox: message not found to mark as PUBLISHED (event_id=%s)", event_id)

            raise OutboxMessageNotFoundException(event_id=event_id)

        try:
            await self._session.flush()

            logger.info("Outbox: message marked as PUBLISHED (event_id=%s)", event_id)

        except SQLAlchemyError as err:
            logger.error(
                "Outbox: flush error while changing status to PUBLISHED! (event_id=%s)",
                message_orm.event_id,
                exc_info=err
            )

            raise err

    async def mark_as_failed(self, event_id: UUID) -> None:
        stmt: Update = (
            update(OutboxMessageModel)
            .where(
                OutboxMessageModel.event_id == event_id,
                OutboxMessageModel.status != MessageStatus.PUBLISHED,
                OutboxMessageModel.status == MessageStatus.PROCESSING,
            )
            .values(status=MessageStatus.FAILED)
            .execution_options(synchronize_session="fetch")
            .returning(OutboxMessageModel)
        )

        result: Result[tuple["OutboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orm: OutboxMessageModel | None = result.scalar_one_or_none()

        if message_orm is None:
            logger.warning("Outbox: message not found to mark as FAILED (event_id=%s)", event_id)

            raise OutboxMessageNotFoundException(event_id=event_id)

        try:
            await self._session.flush()

            logger.info("Outbox: message marked as FAILED (event_id=%s)", event_id)

        except SQLAlchemyError as err:
            logger.error(
                "Outbox: flush error while changing status to FAILED! (event_id=%s)",
                message_orm.event_id,
                exc_info=err
            )

            raise err

    async def to_publish(self) -> list[BaseIntegrationEvent]:
        stmt: Select[tuple["OutboxMessageModel"]] = (
            select(OutboxMessageModel)
            .where(OutboxMessageModel.status == MessageStatus.PENDING)
            .with_for_update(skip_locked=True)
        )

        result: Result[tuple["OutboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orms: list[OutboxMessageModel] = list(result.scalars().all())

        if len(message_orms) == 0:
            logger.debug("Outbox: no pending messages to process")

            return []

        for message_orm in message_orms:
            message_orm.status = MessageStatus.PROCESSING

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                "Outbox: flush error while bulk changing status to PROCESSING!",
                exc_info=err
            )

            raise err

        events: list[BaseIntegrationEvent] = []

        for message_orm in message_orms:
            outbox_message: OutboxMessage = self._model_message_convertor.from_orm(model=message_orm)

            event: BaseIntegrationEvent = self._message_integration_event_convertor.to_event(
                message=outbox_message
            )

            events.append(event)

        return events
