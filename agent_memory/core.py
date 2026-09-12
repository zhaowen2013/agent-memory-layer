from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class MemoryEntry:
    """A single memory record stored in the layer."""

    id: str
    text: str
    vector: Optional[list[float]] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    summary_of: list[str] = field(default_factory=list)  # ids this entry summarizes

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MemoryEntry":
        return cls(**d)


class MemoryError(RuntimeError):
    """Base error for the memory layer."""


def new_id() -> str:
    return uuid.uuid4().hex
