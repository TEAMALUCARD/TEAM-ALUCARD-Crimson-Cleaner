"""
Update Service Stub for Crimson Cleaner.
Prepared for future version checking, remote update API integration, and patch downloads.
"""
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("CrimsonCleaner")


class UpdateService(QObject):
    """Stub service for update management in future versions."""

    update_available = Signal(str, str)  # latest_version, changelog

    def __init__(self, current_version: str = "v0.1.1 Alpha", parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.current_version = current_version

    def check_for_updates(self) -> None:
        """Checks for software updates (Stub implementation)."""
        logger.info("Checking for updates... Current version: %s", self.current_version)
        # Prepared for HTTP API update checks in future versions
