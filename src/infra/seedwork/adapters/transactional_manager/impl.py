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
from infra.seedwork.adapters.log.constants import LogType



logger = logging.getLogger(__name__)


@dataclass
class SQLAlchemyTransactionalManagerImpl:
    _session: AsyncSession

    async def commit(self) -> None:
        try:
            await self._session.commit()

        except SQLAlchemyError as err:
            logger.error(
                msg="Transactional manager: commit error",
                extra={
                    "session_id": id(self._session),
                    "error": str(err),
                    "log_type": LogType.DEV,
                },
                exc_info=True,
            )

            raise TransactionalManagerCommitException() from err

        logger.debug(
            msg="Transactional manager: commit done",
            extra={"log_type": LogType.DEV,},
        )

    async def flush(self) -> None:
        try:
            await self._session.flush()

        except IntegrityError as err:
            logger.error(
                msg="Transactional manager: flush error",
                extra={
                    "session_id": id(self._session),
                    "error": str(err),
                    "log_type": LogType.DEV,
                },
                exc_info=True,
            )

            raise TransactionalManagerIntegrityError() from err

        except SQLAlchemyError as err:
            logger.error(
                msg="Transactional manager: flush error",
                extra={
                    "session_id": id(self._session),
                    "error": str(err),
                    "log_type": LogType.DEV,
                },
                exc_info=True,
            )

            raise TransactionalManagerFlushException() from err

        else:
            logger.debug(
                msg="Transactional manager: flush done",
                extra={"log_type": LogType.DEV,},
            )