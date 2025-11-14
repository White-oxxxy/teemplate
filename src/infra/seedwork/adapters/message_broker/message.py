from abc import ABC
from typing import Any
from uuid import UUID

from msgspec import (
    Struct,
    field,
)
from uuid_utils import uuid7


class Message(
    Struct,
    frozen=True,
    kw_only=True,
    ABC,
):
    id: UUID = field(default_factory=uuid7)
    body: bytes | Any
    partition: int | None = None,
    timestamp_ms: int | None = None,
    headers: dict[str, str] | None = None,