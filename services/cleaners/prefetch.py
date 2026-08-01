"""Read-only scanner for the Windows Prefetch directory."""
from __future__ import annotations

import os
from pathlib import Path

from core.cleaning_models import RiskLevel
from .base import FileSystemCleaningModule


class PrefetchCleaner(FileSystemCleaningModule):
    """Scans Prefetch candidates; future cleanup is classified as normal risk."""

    module_id = "prefetch"
    display_name = "Windows Prefetch"
    risk_level = RiskLevel.NORMAL

    def target_paths(self) -> tuple[Path, ...]:
        return (Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Prefetch",)
