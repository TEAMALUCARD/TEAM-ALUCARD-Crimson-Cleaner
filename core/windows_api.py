"""
Windows API Wrapper for Crimson Cleaner.
Encapsulates Win32 structures and CTypes interfaces for memory and system queries.
Prepared for advanced memory clearing operations in future versions.
"""
import ctypes
from ctypes import wintypes
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("CrimsonCleaner")


class MEMORYSTATUSEX(ctypes.Structure):
    """Win32 MEMORYSTATUSEX structure for detailed memory status queries."""

    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_uint64),
        ("ullAvailPhys", ctypes.c_uint64),
        ("ullTotalPageFile", ctypes.c_uint64),
        ("ullAvailPageFile", ctypes.c_uint64),
        ("ullTotalVirtual", ctypes.c_uint64),
        ("ullAvailVirtual", ctypes.c_uint64),
        ("ullAvailExtendedVirtual", ctypes.c_uint64),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.dwLength = ctypes.sizeof(self)


class WindowsAPI:
    """Provides ctypes wrappers around Windows Kernel32 & Ntdll functions."""

    def __init__(self) -> None:
        self.is_windows = True
        try:
            self.kernel32 = ctypes.windll.kernel32
            self.psapi = ctypes.windll.psapi
        except (AttributeError, OSError) as e:
            logger.warning("Windows API native DLLs not accessible: %s", e)
            self.is_windows = False

    def get_global_memory_status(self) -> Optional[Dict[str, int]]:
        """Retrieves global memory metrics directly via Kernel32 GlobalMemoryStatusEx."""
        if not self.is_windows:
            return None

        mem_status = MEMORYSTATUSEX()
        if self.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status)):
            return {
                "load": mem_status.dwMemoryLoad,
                "total_phys": mem_status.ullTotalPhys,
                "avail_phys": mem_status.ullAvailPhys,
                "total_pagefile": mem_status.ullTotalPageFile,
                "avail_pagefile": mem_status.ullAvailPageFile,
                "total_virtual": mem_status.ullTotalVirtual,
                "avail_virtual": mem_status.ullAvailVirtual,
            }
        else:
            logger.warning("GlobalMemoryStatusEx call failed.")
            return None

    def empty_working_set(self, process_handle: int) -> bool:
        """
        Placeholder method for EmptyWorkingSet Win32 API.
        Prepared for future memory cleaning functionality.
        """
        if not self.is_windows:
            return False
        try:
            return bool(self.psapi.EmptyWorkingSet(process_handle))
        except Exception as e:
            logger.debug("EmptyWorkingSet call failed: %s", e)
            return False
