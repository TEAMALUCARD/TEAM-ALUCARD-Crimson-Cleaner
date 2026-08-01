"""
Custom Primary Button for Crimson Cleaner.
Provides animated glow, hover effects, and modern Crimson styling for "Optimizar Memoria".
"""
from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from ui.theme import COLORS


class PrimaryButton(QPushButton):
    """Vivid Crimson call-to-action button."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(48)
        self._apply_style()

    def _apply_style(self) -> None:
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_hover']}
                );
                color: #FFFFFF;
                font-size: 15px;
                font-weight: 700;
                border: 1px solid {COLORS['primary_hover']};
                border-radius: 8px;
                padding: 0 24px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_hover']}, stop:1 #FF4D6D
                );
                border: 1px solid #FF8095;
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_pressed']};
                border: 1px solid {COLORS['primary']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
            }}
        """)
