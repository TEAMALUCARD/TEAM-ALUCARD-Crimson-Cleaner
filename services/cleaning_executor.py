"""Asynchronous, dry-run-only execution of approved cleaning operations."""
from __future__ import annotations

from dataclasses import replace
import logging
from time import perf_counter

from PySide6.QtCore import QObject, QThread, Signal, Slot

from core.cleaning_execution_models import (
    CleaningExecutionResult,
    CleaningOperation,
    CleaningOperationStatus,
)
from core.workers import WorkerBase

logger = logging.getLogger("CrimsonCleaner")

# This must remain enabled until a future, explicitly approved release introduces
# a separate real-cleaning implementation.
DRY_RUN_EXECUTION = True
_SIMULATED_MESSAGE = "Simulated execution. No changes applied."


class _CleaningExecutionWorker(WorkerBase):
    """Processes operations independently without performing filesystem writes."""

    candidate_started = Signal(CleaningOperation)
    candidate_completed = Signal(CleaningExecutionResult)
    candidate_failed = Signal(CleaningExecutionResult)
    execution_ready = Signal(tuple)

    def __init__(self, operations: tuple[CleaningOperation, ...]) -> None:
        super().__init__("cleaning execution")
        self._operations = operations

    def execute(self) -> tuple[CleaningExecutionResult, ...]:
        results: list[CleaningExecutionResult] = []
        for index, operation in enumerate(self._operations):
            if self.is_cancelled():
                results.extend(self._cancelled_results(self._operations[index:]))
                break

            started_at = perf_counter()
            try:
                result = self._execute_operation(operation, started_at)
            except Exception as error:  # Each candidate failure is deliberately isolated.
                failed_operation = replace(operation, status=CleaningOperationStatus.FAILED)
                result = CleaningExecutionResult(
                    operation=failed_operation,
                    succeeded=False,
                    message="Operation could not be simulated.",
                    duration_seconds=perf_counter() - started_at,
                    error=str(error),
                )
                logger.exception("Dry-run operation failed: %s", operation.id)

            results.append(result)
            if result.succeeded:
                self.candidate_completed.emit(result)
            else:
                self.candidate_failed.emit(result)

        completed_results = tuple(results)
        self.execution_ready.emit(completed_results)
        return completed_results

    def _execute_operation(self, operation: CleaningOperation, started_at: float) -> CleaningExecutionResult:
        if operation.status is not CleaningOperationStatus.APPROVED:
            return CleaningExecutionResult(
                operation=replace(operation, status=CleaningOperationStatus.FAILED),
                succeeded=False,
                message="Operation must be approved before execution.",
                duration_seconds=perf_counter() - started_at,
                error="Operation status is not APPROVED.",
            )

        executing_operation = replace(operation, status=CleaningOperationStatus.EXECUTING)
        self.candidate_started.emit(executing_operation)
        # Intentionally no filesystem access, deletion, elevation, or mutation.
        if not DRY_RUN_EXECUTION:
            raise RuntimeError("Real cleaning is disabled for Crimson Cleaner v0.2 Alpha.")
        return CleaningExecutionResult(
            operation=replace(executing_operation, status=CleaningOperationStatus.COMPLETED),
            succeeded=True,
            message=_SIMULATED_MESSAGE,
            duration_seconds=perf_counter() - started_at,
        )

    @staticmethod
    def _cancelled_results(operations: tuple[CleaningOperation, ...]) -> tuple[CleaningExecutionResult, ...]:
        return tuple(
            CleaningExecutionResult(
                operation=replace(operation, status=CleaningOperationStatus.CANCELLED),
                succeeded=False,
                message="Execution cancelled. No changes applied.",
                duration_seconds=0.0,
            )
            for operation in operations
        )


class CleaningExecutor(QObject):
    """Coordinates an asynchronous dry-run batch using the shared worker base."""

    operation_started = Signal(CleaningOperation)
    operation_completed = Signal(CleaningExecutionResult)
    operation_failed = Signal(CleaningExecutionResult)
    execution_finished = Signal(tuple)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: _CleaningExecutionWorker | None = None
        self._execution_ready = False

    @property
    def is_executing(self) -> bool:
        """Indicates whether an execution worker is currently active."""
        return self._thread is not None and self._thread.isRunning()

    def execute_operations(self, operations: tuple[CleaningOperation, ...]) -> None:
        """Starts a non-destructive asynchronous simulation of the supplied operations."""
        if self.is_executing:
            raise RuntimeError("A cleaning execution is already in progress.")
        self._execution_ready = False
        self._thread = QThread(self)
        self._worker = _CleaningExecutionWorker(tuple(operations))
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.candidate_started.connect(self.operation_started.emit)
        self._worker.candidate_completed.connect(self.operation_completed.emit)
        self._worker.candidate_failed.connect(self.operation_failed.emit)
        self._worker.execution_ready.connect(self._on_execution_ready)
        self._worker.operation_succeeded.connect(self._thread.quit)
        self._worker.operation_cancelled.connect(self._thread.quit)
        self._worker.operation_failed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()

    def cancel_execution(self) -> None:
        """Requests cooperative cancellation; no operation can delete a file."""
        if not self.is_executing or self._execution_ready:
            return
        if self._worker is not None:
            self._worker.cancel()
        if self._thread is not None:
            self._thread.requestInterruption()

    def stop(self) -> None:
        """Cancels an active simulation and waits briefly for its thread."""
        self.cancel_execution()
        if self._thread is not None and not self._thread.wait(5000):
            logger.warning("Cleaning execution worker did not stop within the expected time.")

    @Slot(object)
    def _on_execution_ready(self, results: tuple[CleaningExecutionResult, ...]) -> None:
        self._execution_ready = True
        self.execution_finished.emit(results)

    @Slot()
    def _on_thread_finished(self) -> None:
        if self.sender() is self._thread:
            self._worker = None
            self._thread = None
