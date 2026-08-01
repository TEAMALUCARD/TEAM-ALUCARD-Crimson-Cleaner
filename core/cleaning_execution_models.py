"""Immutable contracts for the non-destructive cleaning execution pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from uuid import uuid4

from core.cleaning_models import RiskLevel


class CleaningOperationAction(str, Enum):
    """Actions that may be enabled by a future cleaning implementation."""

    DELETE = "DELETE"


class CleaningOperationStatus(str, Enum):
    """Lifecycle states for an individual cleaning operation."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class CleaningOperation:
    """A reviewed, immutable candidate for a future cleaning action."""

    module_id: str
    target_path: Path
    proposed_action: CleaningOperationAction
    estimated_size_bytes: int
    risk_level: RiskLevel
    status: CleaningOperationStatus = CleaningOperationStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid4()), kw_only=True)

    def __post_init__(self) -> None:
        if self.estimated_size_bytes < 0:
            raise ValueError("estimated_size_bytes cannot be negative.")


@dataclass(frozen=True, slots=True)
class CleaningExecutionResult:
    """Outcome of one operation, including dry-run failures and cancellation."""

    operation: CleaningOperation
    succeeded: bool
    message: str
    duration_seconds: float
    error: str | None = None

    def __post_init__(self) -> None:
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds cannot be negative.")

