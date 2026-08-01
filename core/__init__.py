"""
Core Package for Crimson Cleaner.
Contains low-level Windows API integration, memory management, process statistics, and logging modules.
"""
from .logger import setup_logger
from .system_info import SystemInfo, MemoryStats
from .memory_manager import MemoryManager
from .process_manager import ProcessManager

__all__ = [
    "setup_logger",
    "SystemInfo",
    "MemoryStats",
    "MemoryManager",
    "ProcessManager",
]
