"""Read-only scanner for common browser cache directories."""
from __future__ import annotations

import os
from pathlib import Path

from core.cleaning_models import RiskLevel
from .base import FileSystemCleaningModule


class BrowserCacheCleaner(FileSystemCleaningModule):
    """Scans known browser cache locations without touching browser data."""

    module_id = "browser_cache"
    display_name = "Browser cache"
    risk_level = RiskLevel.NORMAL

    def target_paths(self) -> tuple[Path, ...]:
        candidates: list[Path] = []
        if local_app_data := os.environ.get("LOCALAPPDATA"):
            local_root = Path(local_app_data)
            candidates.extend((
                local_root / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
                local_root / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
            ))

        if app_data := os.environ.get("APPDATA"):
            profiles_root = Path(app_data) / "Mozilla" / "Firefox" / "Profiles"
            try:
                candidates.extend(profile / "cache2" for profile in profiles_root.iterdir() if profile.is_dir())
            except OSError:
                candidates.append(profiles_root / "cache2")
        return tuple(candidates)
