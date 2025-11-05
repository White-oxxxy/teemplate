from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from uuid import UUID

from infra.seedwork.exception import InfraException


@dataclass(eq=False)
class OutboxException(
    InfraException,
    ABC,
):
    @abstractmethod
    @property
    def message(self) -> str:
        message = f"Outbox exception!"

        return message


@dataclass(eq=False)
class OutboxMessageAlreadyExistException(OutboxException):
    message_id: UUID

    @property
    def message(self) -> str:
        message = f"Message with id {self.message_id} already exist!"

        return message


@dataclass(eq=False)
class CannotMarkPublishedAlreadyPublishedMessageException(OutboxException):
    message_id: UUID

    @property
    def message(self) -> str:
        message = f"Cannot mark PUBLISHED message {self.message_id} (already published)!"

        return message


@dataclass(eq=False)
class OutboxMessageNotFoundException(OutboxException):
    message_id: UUID

    @property
    def message(self) -> str:
        message = f"Message {self.message_id} not found!"

        return message