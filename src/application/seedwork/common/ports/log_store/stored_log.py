from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)
from typing import (
    Any,
    Literal,
    Mapping,
)

from uuid_utils import (
    UUID,
    uuid7,
)


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class StoredLog:
    id: UUID = field(default_factory=uuid7)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    service: str
    module: str
    level: LogLevel
    message: str
    context: Mapping[str, Any] | None = None