from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from domain.seedwork.exception import DomainException


@dataclass(eq=False)
class BusinessRuleException(
    DomainException,
    ABC,
):
    @property
    @abstractmethod
    def message(self) -> str:
        message = f"Business rules exception!"

        return message


@dataclass(eq=False)
class BusinessRuleValidationException(BusinessRuleException):
    message: str

    @property
    def message(self) -> str:
        return self.message