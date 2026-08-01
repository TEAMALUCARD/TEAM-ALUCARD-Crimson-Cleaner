"""
Main Window for Crimson Cleaner.
Combines custom HeaderBar, DashboardView container, frameless window behavior, and system service bindings.
"""
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from services.monitor_service import MonitorService
from services.optimizer_service import OptimizerService
from services.cleaning_service import CleaningService
from ui.widgets.header_bar import HeaderBar
from ui.dashboard import DashboardView
from ui.theme import COLORS


class MainWindow(QMainWindow):
    """Main Application Window."""

    def __init__(
        self,
        monitor_service: MonitorService,
        optimizer_service: OptimizerService,
        cleaning_service: CleaningService,
        version: str = "v0.1.1 Alpha",
        dev: str = "Killgore793",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.monitor_service = monitor_service
        self.optimizer_service = optimizer_service
        self.cleaning_service = cleaning_service

        # Window properties
        self.setWindowTitle("Crimson Cleaner | TEAM ALUCARD")
        self.setMinimumSize(920, 680)
        self.resize(960, 720)

        # Frameless window with custom title bar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Set Window Icon
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        self._setup_ui(version, dev)

    def _setup_ui(self, version: str, dev: str) -> None:
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Bar
        self.header_bar = HeaderBar(
            title="Crimson Cleaner | TEAM ALUCARD",
            version=version,
            dev=dev,
        )
        self.header_bar.minimize_requested.connect(self.showMinimized)
        self.header_bar.close_requested.connect(self.close)

        # Dashboard View
        self.dashboard = DashboardView(
            monitor_service=self.monitor_service,
            optimizer_service=self.optimizer_service,
            cleaning_service=self.cleaning_service,
        )

        main_layout.addWidget(self.header_bar)
        main_layout.addWidget(self.dashboard)

        self.setCentralWidget(central_widget)

    def closeEvent(self, event) -> None:
        """Stops background services before closing."""
        self.monitor_service.stop()
        event.accept()
