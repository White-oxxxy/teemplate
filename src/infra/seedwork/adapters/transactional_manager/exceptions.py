from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from infra.seedwork.exception import InfraException


@dataclass(eq=False)
class TransactionalManagerException(
    InfraException,
    ABC,
):
    @abstractmethod
    @property
    def message(self) -> str:
        message = f"Transactional manager exception!"

        return message


@dataclass(eq=False)
class TransactionalManagerCommitException(TransactionalManagerException):
    @property
    def message(self) -> str:
        message = f"Database query failed. Commit failed."

        return message


@dataclass(eq=False)
class TransactionalManagerFlushException(TransactionalManagerCommitException):
    @property
    def message(self) -> str:
        message = f"Database query failed. Flush failed."

        return message


@dataclass(eq=False)
class TransactionalManagerIntegrityError(TransactionalManagerException):
    @property
    def message(self) -> str:
        message = f"Database constraint violation."

        return message