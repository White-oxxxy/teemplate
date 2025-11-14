from dataclasses import dataclass
from typing import Protocol

from infra.seedwork.adapters.message_broker.message import Message


@dataclass
class MessageBroker(Protocol):
    async def publish_message(
        self,
        key: str | None,
        queue_name: str,
        message: Message,
    ) -> None: ...