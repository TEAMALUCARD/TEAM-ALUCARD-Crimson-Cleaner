"""Read-only safety decisions for future cleaning operations."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import ntpath
import os

from core.cleaning_execution_models import CleaningOperation


class CleaningRiskLevel(str, Enum):
    SAFE = "SAFE"
    NORMAL = "NORMAL"
    ADVANCED = "ADVANCED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class CleaningDecision:
    """Immutable result of evaluating an operation without changing its target."""

    allowed: bool
    requires_backup: bool
    requires_admin: bool
    reason: str
    risk_level: CleaningRiskLevel


class CleaningPolicy:
    """Conservative policy that never accesses or changes the filesystem."""

    _MODULE_RISK_LEVELS = {
        "temp_files": CleaningRiskLevel.SAFE,
        "browser_cache": CleaningRiskLevel.NORMAL,
        "recycle_bin": CleaningRiskLevel.NORMAL,
        "prefetch": CleaningRiskLevel.ADVANCED,
        "windows_update": CleaningRiskLevel.ADVANCED,
    }
    _CRITICAL_FILE_NAMES = frozenset({"bootmgr", "hiberfil.sys", "pagefile.sys", "swapfile.sys"})

    def evaluate(self, operation: CleaningOperation) -> CleaningDecision:
        if self._is_blocked_path(operation):
            return CleaningDecision(False, False, True, "Operation targets a protected Windows system path.", CleaningRiskLevel.BLOCKED)
        risk_level = self._MODULE_RISK_LEVELS.get(operation.module_id, CleaningRiskLevel.NORMAL)
        if risk_level is CleaningRiskLevel.SAFE:
            return CleaningDecision(True, False, False, "Safe temporary-data operation.", risk_level)
        if risk_level is CleaningRiskLevel.NORMAL:
            return CleaningDecision(True, True, False, "Backup preparation required before future execution.", risk_level)
        return CleaningDecision(True, True, True, "Advanced operation requires backup and administrator review.", risk_level)

    def _is_blocked_path(self, operation: CleaningOperation) -> bool:
        target = ntpath.normcase(ntpath.normpath(str(operation.target_path)))
        if ntpath.basename(target) in self._CRITICAL_FILE_NAMES:
            return True
        for directory in self._blocked_directories():
            protected = ntpath.normcase(ntpath.normpath(directory))
            try:
                if ntpath.commonpath((target, protected)) == protected:
                    return True
            except ValueError:
                continue
        return False

    @staticmethod
    def _blocked_directories() -> tuple[str, ...]:
        return (
            os.environ.get("SystemRoot", r"C:\\Windows"),
            os.environ.get("ProgramFiles", r"C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)"),
        )
