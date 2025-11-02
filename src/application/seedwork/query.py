from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Generic,
    TypeVar,
)


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class BaseQuery(ABC): ...


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class BaseQueryResult(ABC): ...


QueryType = TypeVar("QueryType", bound=BaseQuery)
QueryResultType = TypeVar("QueryResultType", bound=BaseQueryResult)


@dataclass
class BaseQueryHandler(
    Generic[QueryType, QueryResultType],
    ABC,
):
    @abstractmethod
    async def handle(self, query: QueryType) -> QueryResultType: ...