"""
Header Bar / Titlebar for Crimson Cleaner.
Displays logo icon, window title "Crimson Cleaner | TEAM ALUCARD",
version badge "v0.1.1 Alpha", developer badge "Dev: Killgore793", and window control buttons.
"""
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QPixmap, QMouseEvent
from ui.theme import COLORS


class HeaderBar(QFrame):
    """Custom frameless header bar with window dragging support."""

    # Window Control Signals
    minimize_requested = Signal()
    close_requested = Signal()

    def __init__(self, title: str = "Crimson Cleaner | TEAM ALUCARD", version: str = "v0.1.1 Alpha", dev: str = "Killgore793", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(54)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

        self._drag_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # App Logo Icon
        self.logo_label = QLabel()
        logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaled(
                28,
                28,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.logo_label.setPixmap(pixmap)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLORS['text_main']};")

        # Version Pill Badge
        self.version_badge = QLabel(version)
        self.version_badge.setObjectName("BadgeLabel")

        # Developer Pill Badge
        self.dev_badge = QLabel(f"Dev: {dev}")
        self.dev_badge.setObjectName("DevBadgeLabel")

        layout.addWidget(self.logo_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.version_badge)
        layout.addWidget(self.dev_badge)
        layout.addStretch()

        # Window Action Buttons (Minimize, Close)
        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(32, 28)
        self.min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.min_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
                color: {COLORS['text_main']};
            }}
        """)
        self.min_btn.clicked.connect(self.minimize_requested.emit)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 28)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
                color: #FFFFFF;
            }}
        """)
        self.close_btn.clicked.connect(self.close_requested.emit)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window:
                self._drag_pos = event.globalPosition().toPoint() - window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos is not None:
            window = self.window()
            if window:
                window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
