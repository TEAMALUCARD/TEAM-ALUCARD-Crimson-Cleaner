"""Reusable Qt worker primitives for non-blocking application operations."""
from __future__ import annotations

import logging
from threading import Event
from time import perf_counter
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal, Slot

logger = logging.getLogger("CrimsonCleaner")


class WorkerBase(QObject):
    """Runs a cancellable operation in a dedicated ``QThread``."""

    operation_started = Signal()
    operation_succeeded = Signal(object, float)
    operation_failed = Signal(str, float)
    operation_cancelled = Signal(float)

    def __init__(self, operation_name: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._operation_name = operation_name
        self._cancel_requested = Event()

    def cancel(self) -> None:
        """Requests cooperative cancellation from any thread."""
        self._cancel_requested.set()

    def is_cancelled(self) -> bool:
        """Returns whether cancellation was requested for this worker."""
        return self._cancel_requested.is_set() or QThread.currentThread().isInterruptionRequested()

    def wait_for_cancellation(self, timeout_seconds: float) -> bool:
        """Waits interruptibly and returns ``True`` when cancellation occurs."""
        return self._cancel_requested.wait(timeout_seconds) or self.is_cancelled()

    @Slot()
    def run(self) -> None:
        """Executes the operation and reports its duration through signals and logs."""
        started_at = perf_counter()
        logger.info("Starting asynchronous operation: %s", self._operation_name)
        self.operation_started.emit()
        try:
            result = self.execute()
        except Exception as error:
            duration_seconds = perf_counter() - started_at
            logger.exception(
                "Asynchronous operation failed: %s (%.3f s)",
                self._operation_name,
                duration_seconds,
            )
            self.operation_failed.emit(str(error), duration_seconds)
            return

        duration_seconds = perf_counter() - started_at
        if self.is_cancelled():
            logger.info("Asynchronous operation cancelled: %s (%.3f s)", self._operation_name, duration_seconds)
            self.operation_cancelled.emit(duration_seconds)
            return

        logger.info("Asynchronous operation completed: %s (%.3f s)", self._operation_name, duration_seconds)
        self.operation_succeeded.emit(result, duration_seconds)

    def execute(self) -> Any:
        """Executes the worker-specific business operation."""
        raise NotImplementedError
