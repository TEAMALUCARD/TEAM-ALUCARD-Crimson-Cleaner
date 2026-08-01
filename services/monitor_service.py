"""System monitoring service executed outside the GUI thread."""
from __future__ import annotations

import logging
from typing import Any, Callable

from PySide6.QtCore import QObject, QThread, Signal, Slot

from core.system_info import MemoryStats, SystemInfo
from core.workers import WorkerBase

logger = logging.getLogger("CrimsonCleaner")


class _MonitorWorker(WorkerBase):
    """Collects system metrics repeatedly without blocking the GUI thread."""

    stats_collected = Signal(object)

    def __init__(self, collector: Callable[[], MemoryStats], interval_ms: int) -> None:
        super().__init__("system monitoring")
        self._collector = collector
        self._interval_seconds = interval_ms / 1000

    def execute(self) -> None:
        while not self.is_cancelled():
            self.stats_collected.emit(self._collector())
            if self.wait_for_cancellation(self._interval_seconds):
                break


class MonitorService(QObject):
    """Coordinates background system monitoring and GUI-safe result signals."""

    stats_updated = Signal(object)

    def __init__(self, interval_ms: int = 1000, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.system_info = SystemInfo()
        self.interval_ms = interval_ms
        self._thread: QThread | None = None
        self._worker: _MonitorWorker | None = None

    def start(self) -> None:
        """Starts system monitoring in a dedicated worker thread."""
        if self._thread is not None and self._thread.isRunning():
            return

        logger.info("Starting System Monitor Service (interval: %d ms)", self.interval_ms)
        self._thread = QThread(self)
        self._worker = _MonitorWorker(self.system_info.get_memory_stats, self.interval_ms)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.stats_collected.connect(self.stats_updated.emit)
        self._worker.operation_succeeded.connect(self._on_worker_stopped)
        self._worker.operation_cancelled.connect(self._on_worker_cancelled)
        self._worker.operation_failed.connect(self._on_worker_failed)
        self._worker.operation_succeeded.connect(self._thread.quit)
        self._worker.operation_cancelled.connect(self._thread.quit)
        self._worker.operation_failed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()

    def stop(self) -> None:
        """Stops monitoring with cooperative cancellation and bounded waiting."""
        if self._thread is None:
            return

        logger.info("Stopping System Monitor Service...")
        self._thread.requestInterruption()
        if self._worker is not None:
            self._worker.cancel()
        self._thread.quit()
        if not self._thread.wait(5000):
            logger.warning("System monitor did not stop within the expected time.")

    def set_interval(self, interval_ms: int) -> None:
        """Updates the interval; it applies when the monitor next starts."""
        self.interval_ms = interval_ms
        if self._thread is not None and self._thread.isRunning():
            logger.warning("The monitor interval will apply on its next start.")

    @Slot(object, float)
    def _on_worker_stopped(self, _: Any, duration_seconds: float) -> None:
        logger.info("System monitor stopped after %.3f s.", duration_seconds)

    @Slot(float)
    def _on_worker_cancelled(self, duration_seconds: float) -> None:
        logger.info("System monitor cancelled after %.3f s.", duration_seconds)

    @Slot(str, float)
    def _on_worker_failed(self, error: str, duration_seconds: float) -> None:
        logger.error("System monitor failed after %.3f s: %s", duration_seconds, error)

    @Slot()
    def _on_thread_finished(self) -> None:
        if self.sender() is self._thread:
            self._worker = None
            self._thread = None
