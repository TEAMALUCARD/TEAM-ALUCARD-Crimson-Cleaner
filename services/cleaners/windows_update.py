"""Read-only scanner for Windows Update download cache candidates."""
from __future__ import annotations

import os
from pathlib import Path

from core.cleaning_models import RiskLevel
from .base import FileSystemCleaningModule


class WindowsUpdateCleaner(FileSystemCleaningModule):
    """Scans Windows Update cache; future cleanup is advanced risk."""

    module_id = "windows_update"
    display_name = "Windows Update cache"
    risk_level = RiskLevel.ADVANCED

    def target_paths(self) -> tuple[Path, ...]:
        windows_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        return (windows_root / "SoftwareDistribution" / "Download",)
