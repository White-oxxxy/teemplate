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
from infra.seedwork.adapters.log.constants import LogType


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
                msg="Outbox: integrity error while adding message!",
                extra={
                    "event_id": event.event_id,
                    "error": str(err),
                    "log_type": LogType.DEV,
                },
                exc_info=True,
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
            logger.debug(
                msg="Outbox: no pending messages",
                extra={"log_type": LogType.DEV,},
            )

            return None

        logger.info(
            msg="Outbox: picked pending message",
            extra={
                "event_id": message_orm.event_id,
                "log_type": LogType.DEV,
            },
        )

        message_orm.status = MessageStatus.PROCESSING

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                msg="Outbox: flush error while changing status to PROCESSING",
                extra={
                    "event_id": message_orm.event_id,
                    "error": str(err),
                    "log_type": LogType.DEV,
                },
                exc_info=True,
            )

            raise

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
            logger.warning(
                msg="Outbox: message not found to mark as PUBLISHED",
                extra={
                    "event_id": event_id,
                    "log_type": LogType.DEV,
                },
            )

            raise OutboxMessageNotFoundException(event_id=event_id)

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                msg="Outbox: flush error while changing status to PUBLISHED",
                extra={
                    "event_id": message_orm.event_id,
                    "error": str(err),
                    "log_type": LogType.DEV,
                },
                exc_info=True,
            )

            raise

        else:
            logger.info(
                msg="Outbox: message marked as PUBLISHED",
                extra={
                    "event_id": event_id,
                    "log_type": LogType.DEV,
                },
            )

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
            logger.warning(
                msg="Outbox: message not found to mark as FAILED",
                extra={
                    "event_id": event_id,
                    "log_type": LogType.DEV,
                },
            )

            raise OutboxMessageNotFoundException(event_id=event_id)

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                msg="Outbox: flush error while changing status to FAILED",
                extra={
                    "event_id": message_orm.event_id,
                    "error": str(err),
                    "log_type": LogType.DEV,
                },
                exc_info=True
            )

            raise

        else:
            logger.info(
                msg="Outbox: message marked as FAILED (event_id=%s)",
                extra={
                    "event_id": event_id,
                    "log_type": LogType.DEV,
                },
            )

    async def to_publish(self) -> list[BaseIntegrationEvent]:
        stmt: Select[tuple["OutboxMessageModel"]] = (
            select(OutboxMessageModel)
            .where(OutboxMessageModel.status == MessageStatus.PENDING)
            .with_for_update(skip_locked=True)
        )

        result: Result[tuple["OutboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orms: list[OutboxMessageModel] = list(result.scalars().all())

        if len(message_orms) == 0:
            logger.debug(
                msg="Outbox: no pending messages to process",
                extra={"log_type": LogType.DEV,},
            )

            return []

        logger.info(
            msg="Outbox: picked pending messages",
            extra={
                "message_count": len(message_orms),
                "log_type": LogType.DEV,
            },
        )

        for message_orm in message_orms:
            message_orm.status = MessageStatus.PROCESSING

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                msg="Outbox: flush error while bulk changing status to PROCESSING!",
                extra={
                    "session_id": id(self._session),
                    "error": str(err),
                    "log_type": LogType.DEV,
                },
                exc_info=True,
            )

            raise

        events: list[BaseIntegrationEvent] = []

        for message_orm in message_orms:
            outbox_message: OutboxMessage = self._model_message_convertor.from_orm(model=message_orm)

            event: BaseIntegrationEvent = self._message_integration_event_convertor.to_event(
                message=outbox_message
            )

            events.append(event)

        return events
