from dataclasses import dataclass
import logging

from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.interfaces.outbox import Outbox


logger = logging.getLogger(__name__)


@dataclass
class EventBusImpl:
    _outbox: Outbox

    async def publish(self, event: DomainEvent) -> None:
        await self._outbox.add(event=event)