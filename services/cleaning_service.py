"""Asynchronous, scan-only orchestration for independent cleaning modules."""
from __future__ import annotations

from collections import deque
from dataclasses import replace
import logging
from time import perf_counter

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot

from core.cleaning_execution_models import CleaningOperation, CleaningOperationAction
from core.cleaning_models import CleaningScanReport, ModuleScanResult, ScanFailure, ScanStatus
from core.workers import WorkerBase
from services.cleaners import BrowserCacheCleaner, PrefetchCleaner, RecycleBinCleaner, TempFilesCleaner, WindowsUpdateCleaner
from services.cleaners.base import CleaningModule

logger = logging.getLogger("CrimsonCleaner")


def _scan_module(module: CleaningModule) -> ModuleScanResult:
    """Scans one module and converts unexpected faults to a typed result."""
    try:
        return module.scan()
    except Exception as error:
        logger.exception("Cleaning module failed: %s", module.module_id)
        return ModuleScanResult(
            module_id=module.module_id,
            display_name=module.display_name,
            risk_level=module.risk_level,
            status=ScanStatus.FAILED,
            locations=(),
            duration_seconds=0.0,
            error_message=str(error),
        )


class _CleaningScanWorker(WorkerBase):
    """Runs a bounded set of module scans away from the GUI thread."""

    module_scanned = Signal(object)
    scan_report_ready = Signal(object)

    def __init__(self, modules: tuple[CleaningModule, ...]) -> None:
        super().__init__("cleaning scan")
        self._modules = modules

    def execute(self) -> CleaningScanReport:
        started_at = perf_counter()
        results: list[ModuleScanResult] = []
        total_modules = len(self._modules)
        for index, module in enumerate(self._modules, start=1):
            if self.is_cancelled():
                report = CleaningScanReport(tuple(results), perf_counter() - started_at, is_cancelled=True)
                self.scan_report_ready.emit(report)
                return report

            result = replace(
                _scan_module(module),
                completed_modules=index,
                total_modules=total_modules,
                progress_percent=int((index / total_modules) * 100) if total_modules else 100,
            )
            results.append(result)
            self.module_scanned.emit(result)

        report = CleaningScanReport(
            results=tuple(results),
            duration_seconds=perf_counter() - started_at,
            is_cancelled=self.is_cancelled(),
        )
        self.scan_report_ready.emit(report)
        return report


class CleaningService(QObject):
    """Coordinates non-blocking safe scans and serializes future scan requests."""

    module_scanned = Signal(object)
    scan_completed = Signal(object)
    scan_failed = Signal(object)

    def __init__(
        self,
        modules: tuple[CleaningModule, ...] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._modules = modules or (
            TempFilesCleaner(),
            PrefetchCleaner(),
            RecycleBinCleaner(),
            WindowsUpdateCleaner(),
            BrowserCacheCleaner(),
        )
        self._thread: QThread | None = None
        self._worker: _CleaningScanWorker | None = None
        self._pending_scans: deque[tuple[CleaningModule, ...]] = deque()
        self._report_ready = False

    @property
    def modules(self) -> tuple[CleaningModule, ...]:
        """Returns registered modules without exposing mutable internal state."""
        return self._modules

    @property
    def is_scanning(self) -> bool:
        """Indicates whether a scan worker is currently running."""
        return self._thread is not None and self._thread.isRunning()

    def start_scan(self, module_ids: tuple[str, ...] | None = None) -> None:
        """Starts a scan or queues it until the active scan finishes."""
        modules = self._resolve_modules(module_ids)
        if self.is_scanning:
            self._pending_scans.append(modules)
            logger.info("Cleaning scan queued; %d request(s) pending.", len(self._pending_scans))
            return
        self._start_worker(modules)

    def cancel_scan(self) -> None:
        """Requests cooperative cancellation of the current scan only."""
        if self._thread is None or not self._thread.isRunning() or self._report_ready:
            return
        logger.info("Cancelling active cleaning scan.")
        self._thread.requestInterruption()
        if self._worker is not None:
            self._worker.cancel()
        self._thread.quit()

    def stop(self) -> None:
        """Cancels the active scan, clears the queue and waits for the worker."""
        self._pending_scans.clear()
        self.cancel_scan()
        if self._thread is not None and not self._thread.wait(5000):
            logger.warning("Cleaning scan worker did not stop within the expected time.")

    def scan_all(self) -> CleaningScanReport:
        """Provides the compatible synchronous engine API for non-UI callers."""
        started_at = perf_counter()
        results = tuple(_scan_module(module) for module in self._modules)
        return CleaningScanReport(results, perf_counter() - started_at)

    def scan_module(self, module_id: str) -> ModuleScanResult:
        """Provides the compatible synchronous API for one non-UI caller."""
        return _scan_module(self._resolve_modules((module_id,))[0])

    def create_operations_from_report(self, report: CleaningScanReport) -> tuple[CleaningOperation, ...]:
        """Builds pending, reviewable operations from an existing scan report.

        Scan locations are aggregate candidates, so this method does not enumerate,
        access, or modify individual files.
        """
        return tuple(
            operation
            for result in report.results
            for operation in self.create_operations_from_result(result)
        )

    @staticmethod
    def create_operations_from_result(result: ModuleScanResult) -> tuple[CleaningOperation, ...]:
        """Builds one pending DELETE candidate per non-empty successful location."""
        if result.status not in (ScanStatus.COMPLETED, ScanStatus.PARTIAL):
            return ()
        return tuple(
            CleaningOperation(
                module_id=result.module_id,
                target_path=location.path,
                proposed_action=CleaningOperationAction.DELETE,
                estimated_size_bytes=location.size_bytes,
                risk_level=result.risk_level,
            )
            for location in result.locations
            if location.error_message is None and location.file_count > 0
        )

    def _resolve_modules(self, module_ids: tuple[str, ...] | None) -> tuple[CleaningModule, ...]:
        if module_ids is None:
            return self._modules
        selected = tuple(module for module in self._modules if module.module_id in module_ids)
        if len(selected) != len(set(module_ids)):
            raise ValueError("One or more requested cleaning modules are not registered.")
        return selected

    def _start_worker(self, modules: tuple[CleaningModule, ...]) -> None:
        logger.info("Starting asynchronous cleaning scan for %d module(s).", len(modules))
        self._report_ready = False
        self._thread = QThread(self)
        self._worker = _CleaningScanWorker(modules)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.module_scanned.connect(self.module_scanned.emit)
        self._worker.scan_report_ready.connect(self._on_scan_report_ready)
        self._worker.operation_succeeded.connect(self._on_worker_succeeded)
        self._worker.operation_cancelled.connect(self._on_worker_cancelled)
        self._worker.operation_failed.connect(self._on_worker_failed)
        self._worker.operation_succeeded.connect(self._thread.quit, Qt.ConnectionType.DirectConnection)
        self._worker.operation_cancelled.connect(self._thread.quit, Qt.ConnectionType.DirectConnection)
        self._worker.operation_failed.connect(self._thread.quit, Qt.ConnectionType.DirectConnection)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()

    @Slot(object, float)
    def _on_worker_succeeded(self, _: object, duration_seconds: float) -> None:
        logger.info("Asynchronous cleaning scan finished in %.3f s.", duration_seconds)

    @Slot(object)
    def _on_scan_report_ready(self, report: CleaningScanReport) -> None:
        """Publishes the typed report and prevents late cancellation during shutdown."""
        self._report_ready = True
        self.scan_completed.emit(report)

    @Slot(float)
    def _on_worker_cancelled(self, duration_seconds: float) -> None:
        logger.info("Asynchronous cleaning scan cancelled in %.3f s.", duration_seconds)

    @Slot(str, float)
    def _on_worker_failed(self, error: str, duration_seconds: float) -> None:
        failure = ScanFailure("cleaning scan", error, duration_seconds)
        logger.error("Asynchronous cleaning scan failed after %.3f s: %s", duration_seconds, error)
        self.scan_failed.emit(failure)

    @Slot()
    def _on_thread_finished(self) -> None:
        if self.sender() is not self._thread:
            return
        self._worker = None
        self._thread = None
        if self._pending_scans:
            self._start_worker(self._pending_scans.popleft())
