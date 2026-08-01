"""Read-only privilege checks for future cleaning operations."""
from __future__ import annotations

import ctypes
import ntpath
import os

from core.cleaning_execution_models import CleaningOperation
from core.cleaning_models import RiskLevel


def is_process_elevated() -> bool:
    """Returns whether the current process has administrative privileges.

    This function only inspects the current security context. It never prompts for
    UAC, restarts the process, or changes privileges.
    """
    if os.name == "nt":
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except (AttributeError, OSError):
            return False
    geteuid = getattr(os, "geteuid", None)
    return bool(geteuid is not None and geteuid() == 0)


def operation_requires_elevation(operation: CleaningOperation) -> bool:
    """Conservatively identifies operations likely to target protected Windows paths."""
    if operation.risk_level is RiskLevel.ADVANCED:
        return True

    target = ntpath.normcase(ntpath.normpath(str(operation.target_path)))
    protected_directories = (
        os.environ.get("SystemRoot", r"C:\\Windows"),
        os.environ.get("ProgramFiles", r"C:\\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)"),
    )
    for directory in protected_directories:
        protected = ntpath.normcase(ntpath.normpath(directory))
        try:
            if ntpath.commonpath((target, protected)) == protected:
                return True
        except ValueError:
            continue
    return False

