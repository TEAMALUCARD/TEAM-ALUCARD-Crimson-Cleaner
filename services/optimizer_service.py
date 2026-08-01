"""Memory optimization service executed outside the GUI thread."""
from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal, Slot

from core.memory_manager import MemoryManager
from core.workers import WorkerBase

logger = logging.getLogger("CrimsonCleaner")


class _OptimizationWorker(WorkerBase):
    """Executes the existing test routine without blocking the GUI thread."""

    progress_changed = Signal(int, str)

    def __init__(self, memory_manager: MemoryManager) -> None:
        super().__init__("memory optimization test")
        self._memory_manager = memory_manager

    def execute(self) -> dict[str, Any]:
        steps = (
            (20, "Analizando Working Sets de procesos activos..."),
            (40, "Verificando lista Standby y memoria en caché..."),
            (60, "Evaluando la paginación de memoria y Commit Limit..."),
            (80, "Simulando liberación de páginas no esenciales..."),
            (100, "Prueba de optimización v0.1.1 Alpha completada con éxito."),
        )
        for percent, message in steps:
            if self.wait_for_cancellation(0.25):
                return {"status": "cancelled"}
            logger.info("Optimization step [%d%%]: %s", percent, message)
            self.progress_changed.emit(percent, message)

        if self.is_cancelled():
            return {"status": "cancelled"}
        return self._memory_manager.simulate_optimization()


class OptimizerService(QObject):
    """Coordinates memory optimization tasks and GUI-safe progress signals."""

    optimization_started = Signal()
    optimization_progress = Signal(int, str)
    optimization_finished = Signal(dict)
    optimization_error = Signal(str)

    def __init__(self, memory_manager: MemoryManager | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.memory_manager = memory_manager or MemoryManager()
        self._is_running = False
        self._thread: QThread | None = None
        self._worker: _OptimizationWorker | None = None

    @property
    def is_running(self) -> bool:
        """Indicates whether an optimization is in progress."""
        return self._is_running

    def run_optimization_test(self) -> None:
        """Launches the compatible v0.1.1 test sequence in a worker thread."""
        if self._is_running:
            logger.warning("Optimization process already in progress.")
            return

        self._is_running = True
        logger.info("Initiating Memory Optimization Test Routine (v0.1.1 Alpha)...")
        self.optimization_started.emit()
        self._thread = QThread(self)
        self._worker = _OptimizationWorker(self.memory_manager)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress_changed.connect(self.optimization_progress.emit)
        self._worker.operation_succeeded.connect(self._on_optimization_succeeded)
        self._worker.operation_failed.connect(self._on_optimization_failed)
        self._worker.operation_cancelled.connect(self._on_optimization_cancelled)
        self._worker.operation_succeeded.connect(self._thread.quit)
        self._worker.operation_failed.connect(self._thread.quit)
        self._worker.operation_cancelled.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()

    def cancel_optimization(self) -> None:
        """Requests cooperative cancellation of the current optimization."""
        if self._thread is None:
            return
        self._thread.requestInterruption()
        if self._worker is not None:
            self._worker.cancel()
        self._thread.quit()

    def stop(self) -> None:
        """Stops the worker thread cleanly during application shutdown."""
        self.cancel_optimization()
        if self._thread is not None and not self._thread.wait(5000):
            logger.warning("Optimizer worker did not stop within the expected time.")

    @Slot(object, float)
    def _on_optimization_succeeded(self, result: dict[str, Any], duration_seconds: float) -> None:
        self._is_running = False
        logger.info("Optimization completed in %.3f s.", duration_seconds)
        self.optimization_finished.emit(result)

    @Slot(str, float)
    def _on_optimization_failed(self, error: str, duration_seconds: float) -> None:
        self._is_running = False
        logger.error("Optimization failed after %.3f s: %s", duration_seconds, error)
        self.optimization_error.emit(error)

    @Slot(float)
    def _on_optimization_cancelled(self, duration_seconds: float) -> None:
        self._is_running = False
        logger.info("Optimization cancelled after %.3f s.", duration_seconds)
        self.optimization_error.emit("Optimization cancelled.")

    @Slot()
    def _on_thread_finished(self) -> None:
        if self.sender() is self._thread:
            self._worker = None
            self._thread = None
