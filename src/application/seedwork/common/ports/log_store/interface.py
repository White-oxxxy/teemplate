from dataclasses import dataclass
from typing import Protocol

from application.seedwork.common.ports.log_store.stored_log import StoredLog


@dataclass
class LogStore(Protocol):
    async def save_logs(self, logs: list[StoredLog]) -> None: ...