"""Common interfaces and read-only filesystem scanning helpers."""
from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from time import perf_counter

from core.cleaning_models import CleanResult, CleanStatus, ModuleScanResult, RiskLevel, ScanLocation, ScanStatus

logger = logging.getLogger("CrimsonCleaner")


class CleaningModule(ABC):
    """Contract implemented by every independently executable cleaning module."""

    module_id: str
    display_name: str
    risk_level: RiskLevel

    @abstractmethod
    def scan(self) -> ModuleScanResult:
        """Returns candidates without modifying the filesystem."""

    def estimate_size(self) -> int:
        """Returns an up-to-date, read-only estimate in bytes."""
        return self.scan().total_size_bytes

    def clean(self, scan_result: ModuleScanResult) -> CleanResult:
        """Reports dry-run-only status; filesystem deletion is intentionally disabled."""
        logger.info("Cleaning blocked in scan-only mode for module %s", self.module_id)
        return CleanResult(
            module_id=self.module_id,
            status=CleanStatus.DRY_RUN_ONLY,
            scanned_size_bytes=scan_result.total_size_bytes,
            message="Cleaning is disabled in Crimson Cleaner v0.2 Alpha scan-only mode.",
        )


class FileSystemCleaningModule(CleaningModule):
    """Reusable, non-destructive scanner for one or more directory locations."""

    def scan(self) -> ModuleScanResult:
        started_at = perf_counter()
        locations: list[ScanLocation] = []
        errors: list[str] = []
        available_locations = 0

        for location_path in self.target_paths():
            location = self._scan_location(location_path)
            locations.append(location)
            if location.error_message is None:
                available_locations += 1
            else:
                errors.append(f"{location.path}: {location.error_message}")

        duration_seconds = perf_counter() - started_at
        if available_locations == 0:
            status = ScanStatus.UNAVAILABLE
        elif errors:
            status = ScanStatus.PARTIAL
        elif any(location.file_count for location in locations):
            status = ScanStatus.COMPLETED
        else:
            status = ScanStatus.EMPTY

        return ModuleScanResult(
            module_id=self.module_id,
            display_name=self.display_name,
            risk_level=self.risk_level,
            status=status,
            locations=tuple(locations),
            duration_seconds=duration_seconds,
            error_message="; ".join(errors) if errors else None,
        )

    @abstractmethod
    def target_paths(self) -> tuple[Path, ...]:
        """Returns candidate directories, without creating or changing them."""

    @staticmethod
    def _scan_location(location_path: Path) -> ScanLocation:
        """Recursively totals regular files without following symlinks or writing data."""
        if not location_path.is_dir():
            return ScanLocation(location_path, 0, 0, "Directory is unavailable.")

        total_size = 0
        file_count = 0
        pending_directories = [location_path]
        try:
            while pending_directories:
                current_directory = pending_directories.pop()
                with os.scandir(current_directory) as entries:
                    for entry in entries:
                        try:
                            if entry.is_dir(follow_symlinks=False):
                                pending_directories.append(Path(entry.path))
                            elif entry.is_file(follow_symlinks=False):
                                total_size += entry.stat(follow_symlinks=False).st_size
                                file_count += 1
                        except OSError as error:
                            logger.debug("Unable to inspect %s: %s", entry.path, error)
        except OSError as error:
            return ScanLocation(location_path, total_size, file_count, str(error))
        return ScanLocation(location_path, total_size, file_count)
