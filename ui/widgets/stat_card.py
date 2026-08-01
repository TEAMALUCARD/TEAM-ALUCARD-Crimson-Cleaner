"""
StatCard Component for Crimson Cleaner.
Displays a metric title, numeric value, subtitle/percentage indicator, and optional mini progress bar.
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar, QWidget
from ui.theme import COLORS


class StatCard(QFrame):
    """Modern card widget for system metrics."""

    def __init__(
        self,
        title: str,
        initial_value: str = "--",
        subtitle: str = "",
        show_progress: bool = False,
        accent_color: str = COLORS["primary"],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.accent_color = accent_color
        self.show_progress = show_progress

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Header Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("SubTitleLabel")

        # Main Value
        self.value_label = QLabel(initial_value)
        self.value_label.setObjectName("ValueLabel")

        # Subtitle / Details
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)

        # Optional Progress Bar
        if show_progress:
            self.progress_bar = QProgressBar()
            self.progress_bar.setFixedHeight(4)
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {COLORS['border']};
                    border: none;
                    border-radius: 2px;
                }}
                QProgressBar::chunk {{
                    background-color: {self.accent_color};
                    border-radius: 2px;
                }}
            """)
            self.progress_bar.setValue(0)
            layout.addWidget(self.progress_bar)

    def update_data(self, value: str, subtitle: str = "", percent: float | None = None) -> None:
        """Updates the displayed value and progress bar."""
        self.value_label.setText(value)
        if subtitle:
            self.subtitle_label.setText(subtitle)

        if self.show_progress and percent is not None:
            clamped_val = max(0, min(100, int(percent)))
            self.progress_bar.setValue(clamped_val)
