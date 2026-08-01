"""Dashboard view that consumes service signals and typed presentation models."""
from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.cleaning_models import CleaningScanReport, ModuleScanResult, ScanFailure
from core.system_info import MemoryStats
from services.cleaning_service import CleaningService
from services.monitor_service import MonitorService
from services.optimizer_service import OptimizerService
from ui.theme import COLORS
from ui.widgets import LogViewer, MemoryBar, PrimaryButton, StatCard

logger = logging.getLogger("CrimsonCleaner")


class DashboardView(QWidget):
    """Main dashboard, updated exclusively through service signals and slots."""

    def __init__(
        self,
        monitor_service: MonitorService,
        optimizer_service: OptimizerService,
        cleaning_service: CleaningService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.monitor_service = monitor_service
        self.optimizer_service = optimizer_service
        self.cleaning_service = cleaning_service
        self._scan_rows: dict[str, int] = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        outer_layout.addWidget(scroll_area)

        content = QWidget()
        scroll_area.setWidget(content)
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 16, 20, 20)
        main_layout.setSpacing(16)

        hero_frame = QFrame()
        hero_frame.setObjectName("DashboardCard")
        hero_layout = QHBoxLayout(hero_frame)
        hero_layout.setContentsMargins(20, 16, 20, 16)
        hero_layout.setSpacing(20)

        hero_info_layout = QVBoxLayout()
        hero_info_layout.setSpacing(4)
        hero_title = QLabel("Optimizador de Memoria RAM")
        hero_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLORS['text_main']};")
        self.status_label = QLabel("Estado: Sistema monitoreado en tiempo real.")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        hero_info_layout.addWidget(hero_title)
        hero_info_layout.addWidget(self.status_label)

        self.optimize_btn = PrimaryButton("⚡ Optimizar Memoria")
        self.optimize_btn.setMinimumWidth(220)
        self.optimize_btn.clicked.connect(self._on_optimize_clicked)
        hero_layout.addLayout(hero_info_layout)
        hero_layout.addStretch()
        hero_layout.addWidget(self.optimize_btn)
        main_layout.addWidget(hero_frame)

        self.memory_bar = MemoryBar()
        main_layout.addWidget(self.memory_bar)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        self.card_installed = StatCard("RAM INSTALADA", "-- GB", "Memoria Física Total", accent_color=COLORS["primary_hover"])
        self.card_used = StatCard("RAM UTILIZADA", "-- GB", "Uso del Sistema", show_progress=True, accent_color=COLORS["primary"])
        self.card_free = StatCard("RAM LIBRE", "-- GB", "Memoria Disponible", accent_color=COLORS["success"])
        self.card_cached = StatCard("MEMORIA EN CACHÉ", "-- GB", "Standby / Cache", accent_color=COLORS["accent_gold"])
        self.card_commit = StatCard("COMMIT LIMIT", "-- GB", "Carga Comprometida")
        self.card_pagefile = StatCard("PAGE FILE", "-- GB", "Archivo de Paginación")
        self.card_cpu = StatCard("USO DE CPU", "-- %", "Procesador Principal", show_progress=True, accent_color=COLORS["primary_hover"])
        self.card_procs = StatCard("PROCESOS", "--", "Tareas Activas Windows", accent_color=COLORS["text_main"])
        cards = (
            self.card_installed, self.card_used, self.card_free, self.card_cached,
            self.card_commit, self.card_pagefile, self.card_cpu, self.card_procs,
        )
        for index, card in enumerate(cards):
            grid_layout.addWidget(card, index // 4, index % 4)
        main_layout.addLayout(grid_layout)

        main_layout.addWidget(self._create_scan_panel())

        self.log_viewer = LogViewer()
        main_layout.addWidget(self.log_viewer)

    def _create_scan_panel(self) -> QFrame:
        """Builds the scan-only section without coupling it to module implementations."""
        scan_frame = QFrame()
        scan_frame.setObjectName("DashboardCard")
        layout = QVBoxLayout(scan_frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        title = QLabel("Análisis seguro del sistema")
        title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COLORS['text_main']};")
        self.scan_mode_label = QLabel("Modo: Análisis (sin cambios en el sistema)")
        self.scan_mode_label.setStyleSheet(f"color: {COLORS['accent_gold']}; font-size: 12px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.scan_mode_label)
        layout.addLayout(header_layout)

        action_layout = QHBoxLayout()
        self.start_scan_button = PrimaryButton("🔍 Analizar sistema")
        self.start_scan_button.setMinimumWidth(210)
        self.start_scan_button.clicked.connect(self._on_scan_requested)
        self.cancel_scan_button = QPushButton("Cancelar")
        self.cancel_scan_button.setEnabled(False)
        self.cancel_scan_button.clicked.connect(self.cleaning_service.cancel_scan)
        self.cancel_scan_button.setStyleSheet(
            f"QPushButton {{ color: {COLORS['text_main']}; background: {COLORS['border']}; "
            f"border: 1px solid {COLORS['border_light']}; border-radius: 6px; padding: 8px 16px; }}"
            f"QPushButton:hover:enabled {{ background: {COLORS['danger']}; }}"
            f"QPushButton:disabled {{ color: {COLORS['text_muted']}; }}"
        )
        action_layout.addWidget(self.start_scan_button)
        action_layout.addWidget(self.cancel_scan_button)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.scan_progress = QProgressBar()
        self.scan_progress.setRange(0, 100)
        self.scan_progress.setValue(0)
        self.scan_progress.setFormat("0%")
        self.scan_progress.setStyleSheet(
            f"QProgressBar {{ background: {COLORS['border']}; border: none; border-radius: 4px; height: 9px; }}"
            f"QProgressBar::chunk {{ background: {COLORS['primary']}; border-radius: 4px; }}"
        )
        layout.addWidget(self.scan_progress)

        self.scan_table = QTableWidget(0, 6)
        self.scan_table.setHorizontalHeaderLabels(("Módulo", "Estado", "Archivos", "Tamaño", "Riesgo", "Duración"))
        self.scan_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.scan_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.scan_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.scan_table.setMinimumHeight(165)
        self.scan_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.scan_table.setStyleSheet(
            f"QTableWidget {{ background: {COLORS['bg_input']}; border: 1px solid {COLORS['border']}; "
            f"gridline-color: {COLORS['border']}; color: {COLORS['text_main']}; }}"
            f"QHeaderView::section {{ background: {COLORS['bg_card']}; color: {COLORS['text_secondary']}; border: none; padding: 5px; }}"
        )
        layout.addWidget(self.scan_table)

        self.scan_summary_label = QLabel("Resumen: esperando inicio de análisis.")
        self.scan_summary_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(self.scan_summary_label)
        return scan_frame

    def _connect_signals(self) -> None:
        """Connects all service events to GUI-thread slots."""
        self.monitor_service.stats_updated.connect(self.update_stats)
        self.optimizer_service.optimization_started.connect(self._on_optimization_started)
        self.optimizer_service.optimization_progress.connect(self._on_optimization_progress)
        self.optimizer_service.optimization_finished.connect(self._on_optimization_finished)
        self.cleaning_service.module_scanned.connect(self._on_module_scanned)
        self.cleaning_service.scan_completed.connect(self._on_scan_completed)
        self.cleaning_service.scan_failed.connect(self._on_scan_failed)

    @Slot(object)
    def update_stats(self, stats: MemoryStats) -> None:
        """Updates system cards from the current typed monitoring snapshot."""
        if not stats.is_available:
            self.status_label.setText("Estado: métricas del sistema no disponibles.")
            return
        self.card_installed.update_data(f"{stats.total_ram_gb:.2f} GB", "Memoria Física")
        self.card_used.update_data(f"{stats.used_ram_gb:.2f} GB", f"{stats.ram_usage_percent:.1f}% en uso", percent=stats.ram_usage_percent)
        self.card_free.update_data(f"{stats.free_ram_gb:.2f} GB", "Disponible inmediato")
        self.card_cached.update_data(f"{stats.cached_ram_gb:.2f} GB", "En espera OS")
        self.card_commit.update_data(f"{stats.commit_used_gb:.2f} GB", f"De {stats.commit_total_gb:.2f} GB")
        self.card_pagefile.update_data(f"{stats.pagefile_used_gb:.2f} GB", f"De {stats.pagefile_total_gb:.2f} GB")
        self.card_cpu.update_data(f"{stats.cpu_percent:.1f} %", "Carga actual", percent=stats.cpu_percent)
        self.card_procs.update_data(f"{stats.process_count}", "Hilos / PIDs activos")
        self.memory_bar.update_distribution(stats.total_ram_gb, stats.used_ram_gb, stats.cached_ram_gb, stats.free_ram_gb)

    @Slot()
    def _on_scan_requested(self) -> None:
        self._scan_rows.clear()
        self.scan_table.setRowCount(0)
        self.scan_progress.setValue(0)
        self.start_scan_button.setEnabled(False)
        self.cancel_scan_button.setEnabled(True)
        self.scan_summary_label.setText("Resumen: análisis en curso, sin cambios en el sistema.")
        self.cleaning_service.start_scan()

    @Slot(object)
    def _on_module_scanned(self, result: ModuleScanResult) -> None:
        row = self._scan_rows.get(result.module_id)
        if row is None:
            row = self.scan_table.rowCount()
            self._scan_rows[result.module_id] = row
            self.scan_table.insertRow(row)
        values = (
            result.display_name,
            result.status.value.upper(),
            str(result.total_file_count),
            self._format_size(result.total_size_bytes),
            result.risk_level.value.upper(),
            f"{result.duration_seconds:.3f} s",
        )
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column == 0:
                item.setData(Qt.ItemDataRole.UserRole, result)
                item.setToolTip("Resultado preparado para futuras acciones de detalle.")
            self.scan_table.setItem(row, column, item)
        self.scan_progress.setValue(result.progress_percent)

    @Slot(object)
    def _on_scan_completed(self, report: CleaningScanReport) -> None:
        self.start_scan_button.setEnabled(True)
        self.cancel_scan_button.setEnabled(False)
        self.scan_progress.setValue(100 if not report.is_cancelled else self.scan_progress.value())
        final_status = "cancelado" if report.is_cancelled else "completado"
        self.scan_summary_label.setText(
            "Resumen: "
            f"{report.module_count} módulos analizados | "
            f"{report.failed_module_count} con errores | "
            f"{self._format_size(report.total_size_bytes)} recuperables | "
            f"{report.total_file_count} archivos | "
            f"{report.duration_seconds:.3f} s | Estado: {final_status}."
        )

    @Slot(object)
    def _on_scan_failed(self, failure: ScanFailure) -> None:
        self.start_scan_button.setEnabled(True)
        self.cancel_scan_button.setEnabled(False)
        self.scan_summary_label.setText(f"Resumen: análisis no completado ({failure.error_message}).")

    def _on_optimize_clicked(self) -> None:
        """Starts the existing optimization workflow."""
        self.optimizer_service.run_optimization_test()

    def _on_optimization_started(self) -> None:
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.setText("⏳ Optimizando...")
        self.status_label.setText("Estado: Ejecutando rutina de prueba v0.1.1 Alpha...")

    def _on_optimization_progress(self, percent: int, message: str) -> None:
        self.status_label.setText(f"Estado [{percent}%]: {message}")

    def _on_optimization_finished(self, result: dict) -> None:
        self.optimize_btn.setEnabled(True)
        self.optimize_btn.setText("⚡ Optimizar Memoria")
        freed_mb = result.get("simulated_freed_mb", 0.0)
        self.status_label.setText(f"Estado: Prueba completada. Ganancia estimada: {freed_mb} MB.")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Formats a model-provided byte value for display only."""
        value = float(size_bytes)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                return f"{value:.2f} {unit}"
            value /= 1024
        return "0 B"
