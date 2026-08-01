"""Read-only scanner for user and Windows temporary files."""
from __future__ import annotations

import os
from pathlib import Path

from core.cleaning_models import RiskLevel
from .base import FileSystemCleaningModule


class TempFilesCleaner(FileSystemCleaningModule):
    """Scans temporary directories without deleting their contents."""

    module_id = "temp_files"
    display_name = "Temporary files"
    risk_level = RiskLevel.SAFE

    def target_paths(self) -> tuple[Path, ...]:
        windows_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        environment_paths = tuple(
            Path(value)
            for variable in ("TEMP", "TMP")
            if (value := os.environ.get(variable))
        )
        return tuple(dict.fromkeys((*environment_paths, windows_root / "Temp")))
