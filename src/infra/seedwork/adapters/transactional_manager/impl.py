from dataclasses import dataclass
import logging

from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from infra.seedwork.adapters.transactional_manager.exceptions import (
    TransactionalManagerCommitException,
    TransactionalManagerFlushException,
    TransactionalManagerIntegrityError,
)


logger = logging.getLogger(__name__)


@dataclass
class SQLAlchemyTransactionalManagerImpl:
    _session: AsyncSession

    async def commit(self) -> None:
        try:
            await self._session.commit()

            logger.debug("Commit done!")

        except SQLAlchemyError as err:

            raise TransactionalManagerCommitException() from err

    async def flush(self) -> None:
        try:
            await self._session.flush()

            logger.debug("Flush done!")

        except IntegrityError as err:

            raise TransactionalManagerIntegrityError() from err

        except SQLAlchemyError as err:

            raise TransactionalManagerFlushException() from err