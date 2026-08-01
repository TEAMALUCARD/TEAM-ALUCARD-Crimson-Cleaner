"""Typed contracts shared by the cleaning scan engine and its modules."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RiskLevel(str, Enum):
    """Risk classification used by future cleaning profiles."""

    SAFE = "safe"
    NORMAL = "normal"
    ADVANCED = "advanced"


class ScanStatus(str, Enum):
    """Terminal states for a module scan."""

    COMPLETED = "completed"
    EMPTY = "empty"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


class CleanStatus(str, Enum):
    """Terminal states for a cleaning request."""

    DRY_RUN_ONLY = "dry_run_only"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class ScanLocation:
    """Aggregated scan data for a single filesystem location."""

    path: Path
    size_bytes: int
    file_count: int
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class ModuleScanResult:
    """Typed, read-only result from one cleaning module."""

    module_id: str
    display_name: str
    risk_level: RiskLevel
    status: ScanStatus
    locations: tuple[ScanLocation, ...]
    duration_seconds: float
    error_message: str | None = None
    completed_modules: int = 0
    total_modules: int = 0
    progress_percent: int = 0

    @property
    def total_size_bytes(self) -> int:
        """Returns the total candidate size across successfully scanned locations."""
        return sum(location.size_bytes for location in self.locations)

    @property
    def total_file_count(self) -> int:
        """Returns the number of candidate files across scanned locations."""
        return sum(location.file_count for location in self.locations)


@dataclass(frozen=True, slots=True)
class CleaningScanReport:
    """Result from a complete engine scan."""

    results: tuple[ModuleScanResult, ...]
    duration_seconds: float
    is_cancelled: bool = False

    @property
    def total_size_bytes(self) -> int:
        """Returns the total candidate size reported by all modules."""
        return sum(result.total_size_bytes for result in self.results)

    @property
    def module_count(self) -> int:
        """Returns the number of modules represented by this report."""
        return len(self.results)

    @property
    def failed_module_count(self) -> int:
        """Returns the number of modules that could not complete."""
        return sum(result.status is ScanStatus.FAILED for result in self.results)

    @property
    def total_file_count(self) -> int:
        """Returns the number of candidate files across all modules."""
        return sum(result.total_file_count for result in self.results)


@dataclass(frozen=True, slots=True)
class ScanFailure:
    """Typed error emitted when an asynchronous scan cannot complete."""

    operation_name: str
    error_message: str
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class CleanResult:
    """Safe response to a cleaning request while destructive cleaning is disabled."""

    module_id: str
    status: CleanStatus
    scanned_size_bytes: int
    message: str
