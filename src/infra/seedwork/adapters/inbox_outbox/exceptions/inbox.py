from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from uuid import UUID

from infra.seedwork.exception import InfraException


@dataclass(eq=False)
class InboxException(
    InfraException,
    ABC,
):
    @abstractmethod
    @property
    def message(self) -> str:
        message = f"Inbox exception!"

        return message


@dataclass(eq=False)
class InboxMessageAlreadyExistException(InboxException):
    event_id: UUID

    @property
    def message(self) -> str:
        message = f"Message with event id {self.event_id} already exist!"

        return message


@dataclass(eq=False)
class InboxMessageNotFoundException(InboxException):
    event_id: UUID

    @property
    def message(self) -> str:
        message = f"Message with event id {self.event_id} not found!"

        return message