"""Portable audit contracts for the cleaning execution pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class CleaningAuditEntry:
    """One immutable execution record, ready for a future export adapter."""

    timestamp: datetime
    operation_id: str
    module: str
    path: str
    action: str
    result: str
    duration_seconds: float
    message: str
