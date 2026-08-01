"""
MemoryBar Component for Crimson Cleaner.
Provides a segmented visual representation of RAM allocation (Used, Cached, Free).
"""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ui.theme import COLORS


class MemoryBar(QFrame):
    """Segmented visual progress bar for RAM distribution."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardCard")
        self.setFixedHeight(84)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Title and legend header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Distribución de Memoria RAM")
        title.setStyleSheet(f"font-weight: 600; color: {COLORS['text_main']}; font-size: 13px;")

        self.legend_label = QLabel("Usada: --% | Caché: --% | Libre: --%")
        self.legend_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.legend_label)

        layout.addLayout(header_layout)

        # Segmented bar container
        self.bar_container = QFrame()
        self.bar_container.setFixedHeight(12)
        self.bar_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['border']};
                border-radius: 6px;
            }}
        """)

        self.bar_layout = QHBoxLayout(self.bar_container)
        self.bar_layout.setContentsMargins(0, 0, 0, 0)
        self.bar_layout.setSpacing(2)

        # Used Segment (Crimson)
        self.seg_used = QFrame()
        self.seg_used.setStyleSheet(f"background-color: {COLORS['primary']}; border-top-left-radius: 6px; border-bottom-left-radius: 6px;")

        # Cached Segment (Warning/Gold)
        self.seg_cached = QFrame()
        self.seg_cached.setStyleSheet(f"background-color: {COLORS['accent_gold']};")

        # Free Segment (Muted Dark/Success)
        self.seg_free = QFrame()
        self.seg_free.setStyleSheet(f"background-color: {COLORS['border_light']}; border-top-right-radius: 6px; border-bottom-right-radius: 6px;")

        self.bar_layout.addWidget(self.seg_used, 50)
        self.bar_layout.addWidget(self.seg_cached, 20)
        self.bar_layout.addWidget(self.seg_free, 30)

        layout.addWidget(self.bar_container)

    def update_distribution(self, total_gb: float, used_gb: float, cached_gb: float, free_gb: float) -> None:
        """Updates segment ratios dynamically."""
        if total_gb <= 0:
            return

        pct_used = max(0, min(100, int((used_gb / total_gb) * 100)))
        pct_cached = max(0, min(100, int((cached_gb / total_gb) * 100)))
        pct_free = max(0, 100 - pct_used - pct_cached)

        self.legend_label.setText(
            f"Usada: {used_gb:.2f} GB ({pct_used}%) | "
            f"Caché: {cached_gb:.2f} GB ({pct_cached}%) | "
            f"Libre: {free_gb:.2f} GB ({pct_free}%)"
        )

        self.bar_layout.setStretch(0, max(1, pct_used))
        self.bar_layout.setStretch(1, max(1, pct_cached))
        self.bar_layout.setStretch(2, max(1, pct_free))
