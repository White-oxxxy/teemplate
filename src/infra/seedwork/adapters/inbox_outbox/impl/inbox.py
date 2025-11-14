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

from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent
from infra.seedwork.adapters.inbox_outbox.message import (
    InboxMessage,
    MessageStatus,
)
from infra.seedwork.db.models.inbox import InboxMessageModel
from infra.seedwork.db.convertors.inbox import InboxMessageModelConvertor
from infra.seedwork.adapters.inbox_outbox.convertors.inbox import IntegrationEventInboxMessageConvertor
from infra.seedwork.adapters.inbox_outbox.exceptions.inbox import (
    InboxMessageAlreadyExistException,
    InboxMessageNotFoundException,
)


logger = logging.getLogger(__name__)


@dataclass
class SQLAlchemyInboxImpl:
    _session: AsyncSession
    _model_message_convertor: InboxMessageModelConvertor
    _integration_event_message_convertor: IntegrationEventInboxMessageConvertor

    async def add(self, event: BaseIntegrationEvent) -> None:
        message: InboxMessage = self._integration_event_message_convertor.to_message(event=event)

        message_orm: InboxMessageModel = self._model_message_convertor.to_orm(message=message)

        self._session.add(message_orm)

        try:
            await self._session.flush()

        except IntegrityError as err:
            logger.error(
                "Inbox: integrity error while adding message (event_id=%s): %s",
                event.event_id,
                exc_info=err,
            )

            raise InboxMessageAlreadyExistException(event_id=event.event_id) from err

    async def get_next_pending(self) -> BaseIntegrationEvent | None:
        stmt: Select[tuple["InboxMessageModel"]] = (
            select(InboxMessageModel)
            .where(InboxMessageModel.status == MessageStatus.PENDING)
            .order_by(InboxMessageModel.event_created_at.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )

        result: Result[tuple["InboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orm: InboxMessageModel | None = result.scalar_one_or_none()

        if message_orm is None:
            logger.debug("Inbox: no pending messages")

            return None

        logger.info("Inbox: picked pending message event_id=%s", message_orm.event_id)

        message_orm.status = MessageStatus.PROCESSING

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                "Inbox: flush error while changing status to PROCESSING! (event_id=%s)",
                message_orm.event_id,
                exc_info=err
            )

            raise err

        message: InboxMessage = self._model_message_convertor.from_orm(model=message_orm)

        event: BaseIntegrationEvent = self._integration_event_message_convertor.to_event(
            message=message
        )

        return event

    async def mark_as_processed(self, event_id: UUID) -> None:
        stmt: Update = (
            update(InboxMessageModel)
            .where(
                InboxMessageModel.event_id == event_id,
                InboxMessageModel.status != MessageStatus.PROCESSED,
                InboxMessageModel.status == MessageStatus.PROCESSING,
            )
            .values(status=MessageStatus.PUBLISHED)
            .execution_options(synchronize_session="fetch")
            .returning(InboxMessageModel)
        )

        result: Result[tuple["InboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orm: InboxMessageModel | None = result.scalar_one_or_none()

        if message_orm is None:
            logger.warning("Inbox: message not found to mark as PROCESSED! (event_id=%s)", event_id)

            raise InboxMessageNotFoundException(event_id=event_id)

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                "Inbox: flush error while changing status to PROCESSED! (event_id=%s)",
                message_orm.event_id,
                exc_info=err
            )

            raise err

        else:
            logger.info("Inbox: message marked as PROCESSED! (event_id=%s)", event_id)

    async def mark_as_failed(self, event_id: UUID) -> None:
        stmt: Update = (
            update(InboxMessageModel)
            .where(
                InboxMessageModel.event_id == event_id,
                InboxMessageModel.status != MessageStatus.PUBLISHED,
                InboxMessageModel.status == MessageStatus.PROCESSING,
            )
            .values(status=MessageStatus.FAILED)
            .execution_options(synchronize_session="fetch")
            .returning(InboxMessageModel)
        )

        result: Result[tuple["InboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orm: InboxMessageModel | None = result.scalar_one_or_none()

        if message_orm is None:
            logger.warning("Inbox: message not found to mark as FAILED (event_id=%s)", event_id)

            raise InboxMessageNotFoundException(event_id=event_id)

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                "Inbox: flush error while changing status to FAILED! (event_id=%s)",
                message_orm.event_id,
                exc_info=err
            )

            raise err

        else:
            logger.info("Inbox: message marked as FAILED (event_id=%s)", event_id)

    async def to_processed(self) -> list[BaseIntegrationEvent]:
        stmt: Select[tuple["InboxMessageModel"]] = (
            select(InboxMessageModel)
            .where(InboxMessageModel.status == MessageStatus.PENDING)
            .with_for_update(skip_locked=True)
        )

        result: Result[tuple["InboxMessageModel"]] = await self._session.execute(statement=stmt)

        message_orms: list[InboxMessageModel] = list(result.scalars().all())

        for message_orm in message_orms:
            message_orm.status = MessageStatus.PROCESSING

        try:
            await self._session.flush()

        except SQLAlchemyError as err:
            logger.error(
                "Inbox: flush error while bulk changing status to PROCESSING!",
                exc_info=err
            )

            raise err

        events: list[BaseIntegrationEvent] = []

        for message_orm in message_orms:
            inbox_message: InboxMessage = self._model_message_convertor.from_orm(model=message_orm)

            event: BaseIntegrationEvent = self._integration_event_message_convertor.to_event(
                message=inbox_message
            )

            events.append(event)

        return events