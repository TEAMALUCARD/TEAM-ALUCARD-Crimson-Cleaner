"""Read-only scanner for the current system drive recycle bin."""
from __future__ import annotations

import os
from pathlib import Path

from core.cleaning_models import RiskLevel
from .base import FileSystemCleaningModule


class RecycleBinCleaner(FileSystemCleaningModule):
    """Scans the recycle bin; cleanup remains disabled in this release."""

    module_id = "recycle_bin"
    display_name = "Recycle Bin"
    risk_level = RiskLevel.NORMAL

    def target_paths(self) -> tuple[Path, ...]:
        system_drive = Path(os.environ.get("SystemDrive", "C:"))
        return (system_drive / "$Recycle.Bin",)
