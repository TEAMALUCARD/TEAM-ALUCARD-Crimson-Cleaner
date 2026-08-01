"""
Process Manager for Crimson Cleaner.
Provides utility methods for process enumeration and resource consumption tracking.
Prepared for process-level memory trimming in future releases.
"""
import logging
from typing import List, Dict, Any
import psutil

logger = logging.getLogger("CrimsonCleaner")


class ProcessManager:
    """Manages system process queries and top memory consumer tracking."""

    def get_process_count(self) -> int:
        """Returns total active system process count."""
        try:
            return len(psutil.pids())
        except Exception as e:
            logger.error("Error retrieving process count: %s", e)
            return 0

    def get_top_memory_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns the top N processes consuming the highest RAM."""
        processes = []
        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                mem_info = proc.info.get("memory_info")
                rss = mem_info.rss if mem_info else 0
                processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"] or "Unknown",
                    "ram_bytes": rss,
                    "ram_mb": rss / (1024 * 1024),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug("Failed fetching process info for PID %s: %s", getattr(proc, "pid", "N/A"), e)

        processes.sort(key=lambda p: p["ram_bytes"], reverse=True)
        return processes[:limit]
