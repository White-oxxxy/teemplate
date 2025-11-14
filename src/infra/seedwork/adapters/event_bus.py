from dataclasses import dataclass
import logging

from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.interfaces.outbox import Outbox
from infra.seedwork.adapters.inbox_outbox.exceptions.outbox import OutboxException


logger = logging.getLogger(__name__)


@dataclass
class EventBusImpl:
    _outbox: Outbox

    async def publish(self, event: DomainEvent) -> None:
        try:
            await self._outbox.add(event=event)

        except OutboxException as err:
            logger.error(
                msg="Event bus: Failed to send event to outbox",
                extra={
                    "event_name": event.__class__.__name__,
                    "error": str(err),
                },
                exc_info=True,
            )

            raise

        else:
            logger.debug(
                msg="Event sent to outbox",
                extra={"event_name": event.__class__.__name__},
            )