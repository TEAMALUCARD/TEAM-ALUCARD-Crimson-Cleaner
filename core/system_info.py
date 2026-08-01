"""
System Info Collector for Crimson Cleaner.
Retrieves accurate system hardware, memory (RAM, Cached, Commit, PageFile), CPU usage, and process stats.
"""
from dataclasses import dataclass
import logging
import psutil

from .windows_api import WindowsAPI

logger = logging.getLogger("CrimsonCleaner")


@dataclass
class MemoryStats:
    """Dataclass holding detailed real-time memory metrics."""

    total_ram_bytes: int
    used_ram_bytes: int
    free_ram_bytes: int
    cached_ram_bytes: int
    ram_usage_percent: float
    commit_total_bytes: int
    commit_used_bytes: int
    pagefile_total_bytes: int
    pagefile_used_bytes: int
    cpu_percent: float
    process_count: int
    is_available: bool = True
    error_message: str | None = None

    @property
    def total_ram_gb(self) -> float:
        return self.total_ram_bytes / (1024**3)

    @property
    def used_ram_gb(self) -> float:
        return self.used_ram_bytes / (1024**3)

    @property
    def free_ram_gb(self) -> float:
        return self.free_ram_bytes / (1024**3)

    @property
    def cached_ram_gb(self) -> float:
        return self.cached_ram_bytes / (1024**3)

    @property
    def commit_total_gb(self) -> float:
        return self.commit_total_bytes / (1024**3)

    @property
    def commit_used_gb(self) -> float:
        return self.commit_used_bytes / (1024**3)

    @property
    def pagefile_total_gb(self) -> float:
        return self.pagefile_total_bytes / (1024**3)

    @property
    def pagefile_used_gb(self) -> float:
        return self.pagefile_used_bytes / (1024**3)


class SystemInfo:
    """Gathers live performance metrics from Windows and psutil."""

    def __init__(self) -> None:
        self.win_api = WindowsAPI()

    def get_memory_stats(self) -> MemoryStats:
        """Queries the OS and returns a snapshot of memory and CPU statistics."""
        try:
            svmem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            cpu_pct = psutil.cpu_percent(interval=None)
            proc_cnt = len(psutil.pids())

            # Cached RAM estimation (psutil cached/buffers or windows api calculation)
            cached_bytes = getattr(svmem, "cached", getattr(svmem, "buffers", 0))
            if cached_bytes == 0:
                # Approximate Standby / Cached memory: Total - Available - (Total - Free) if available differs
                cached_bytes = max(0, svmem.available - svmem.free)

            # Native Win32 API metrics if available
            win_stats = self.win_api.get_global_memory_status()
            if win_stats:
                pagefile_total = win_stats["total_pagefile"]
                pagefile_avail = win_stats["avail_pagefile"]
                pagefile_used = max(0, pagefile_total - pagefile_avail)
                # Commit memory total is phys + pagefile
                commit_total = pagefile_total
                commit_used = commit_total - pagefile_avail
            else:
                pagefile_total = swap.total
                pagefile_used = swap.used
                commit_total = svmem.total + swap.total
                commit_used = svmem.used + swap.used

            return MemoryStats(
                total_ram_bytes=svmem.total,
                used_ram_bytes=svmem.used,
                free_ram_bytes=svmem.available,
                cached_ram_bytes=cached_bytes,
                ram_usage_percent=svmem.percent,
                commit_total_bytes=commit_total,
                commit_used_bytes=commit_used,
                pagefile_total_bytes=pagefile_total,
                pagefile_used_bytes=pagefile_used,
                cpu_percent=cpu_pct,
                process_count=proc_cnt,
            )
        except (OSError, psutil.Error) as error:
            logger.error("Unable to gather memory statistics: %s", error)
            return MemoryStats(
                total_ram_bytes=0,
                used_ram_bytes=0,
                free_ram_bytes=0,
                cached_ram_bytes=0,
                ram_usage_percent=0.0,
                commit_total_bytes=0,
                commit_used_bytes=0,
                pagefile_total_bytes=0,
                pagefile_used_bytes=0,
                cpu_percent=0.0,
                process_count=0,
                is_available=False,
                error_message=str(error),
            )
