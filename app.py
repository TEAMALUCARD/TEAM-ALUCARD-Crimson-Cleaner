"""
CrimsonCleanerApp - Application Controller for Crimson Cleaner.
Subclasses PySide6 QApplication, initializes services, logging, config manager, and shows MainWindow.
"""
from PySide6.QtWidgets import QApplication
import logging

from config.config_manager import ConfigManager
from core.logger import setup_logger
from services.monitor_service import MonitorService
from services.optimizer_service import OptimizerService
from services.cleaning_service import CleaningService
from services.update_service import UpdateService
from ui.main_window import MainWindow
from ui.theme import get_application_stylesheet


class CrimsonCleanerApp(QApplication):
    """Main Application Controller."""

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)

        # Application metadata
        self.setApplicationName("Crimson Cleaner")
        self.setOrganizationName("TEAM ALUCARD")

        self.config_manager = ConfigManager()
        log_level = getattr(logging, str(self.config_manager.get("log_level", "INFO")).upper(), logging.INFO)
        self.logger = setup_logger("CrimsonCleaner", level=log_level)
        self.logger.info("==========================================")
        self.logger.info("Starting Crimson Cleaner | TEAM ALUCARD v0.1.1 Alpha")
        self.logger.info("Developer: Killgore793")
        self.logger.info("==========================================")

        # Instantiate Services
        refresh_interval = self.config_manager.refresh_interval_ms
        self.monitor_service = MonitorService(interval_ms=refresh_interval)
        self.optimizer_service = OptimizerService()
        self.cleaning_service = CleaningService()
        self.update_service = UpdateService(current_version=self.config_manager.version)
        self.aboutToQuit.connect(self._shutdown_services)

        # Apply Global Fluent Stylesheet
        self.setStyleSheet(get_application_stylesheet())

        # Initialize Main Window
        self.main_window = MainWindow(
            monitor_service=self.monitor_service,
            optimizer_service=self.optimizer_service,
            cleaning_service=self.cleaning_service,
            version=self.config_manager.version,
            dev=self.config_manager.developer,
        )

    def run(self) -> int:
        """Starts monitoring service and launches Qt Event Loop."""
        self.monitor_service.start()
        self.main_window.show()
        return self.exec()

    def _shutdown_services(self) -> None:
        """Requests a graceful shutdown for all application worker threads."""
        self.monitor_service.stop()
        self.optimizer_service.stop()
        self.cleaning_service.stop()
