from dataclasses import dataclass
from typing import Protocol


@dataclass
class BaseReader(Protocol): ...