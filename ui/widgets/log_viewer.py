"""Qt-safe presentation of records from the central application logger."""
from __future__ import annotations

import html
import logging
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget

from ui.theme import COLORS


class _LogEmitter(QObject):
    """Transfers standard logging records safely to the Qt GUI thread."""

    record_emitted = Signal(object)


class _QtLogHandler(logging.Handler):
    """Logging handler that forwards records without writing to widgets directly."""

    def __init__(self, emitter: _LogEmitter) -> None:
        super().__init__()
        self._emitter = emitter

    def emit(self, record: logging.LogRecord) -> None:
        self._emitter.record_emitted.emit(record)


class LogViewer(QFrame):
    """Embedded console driven exclusively by the central logger."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LogCard")
        self._logger = logging.getLogger("CrimsonCleaner")
        self._emitter = _LogEmitter(self)
        self._handler = _QtLogHandler(self._emitter)
        self._handler.setLevel(logging.DEBUG)
        self._emitter.record_emitted.connect(self._append_record)
        self._logger.addHandler(self._handler)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        header_layout = QHBoxLayout()
        title = QLabel("Registro de Eventos")
        title.setStyleSheet(f"font-weight: 600; color: {COLORS['text_main']}; font-size: 13px;")
        subtitle = QLabel("logger central")
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)

        self.console = QTextEdit()
        self.console.setObjectName("LogConsole")
        self.console.setReadOnly(True)
        self.console.setFixedHeight(120)
        layout.addWidget(self.console)

    @Slot(object)
    def _append_record(self, record: logging.LogRecord) -> None:
        """Formats a central log record after Qt delivers it to the GUI thread."""
        level = record.levelname.upper()
        color_map = {
            "DEBUG": COLORS["text_muted"],
            "INFO": COLORS["text_secondary"],
            "WARNING": COLORS["warning"],
            "ERROR": COLORS["danger"],
            "CRITICAL": COLORS["danger"],
        }
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        message = html.escape(record.getMessage())
        color = color_map.get(level, COLORS["text_main"])
        self.console.append(
            f'<span style="color: {COLORS["text_muted"]};">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: bold;">[{level}]</span> '
            f'<span style="color: {COLORS["text_main"]};">{message}</span>'
        )
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event) -> None:
        """Detaches the presentation handler without changing central logging."""
        self._logger.removeHandler(self._handler)
        super().closeEvent(event)
