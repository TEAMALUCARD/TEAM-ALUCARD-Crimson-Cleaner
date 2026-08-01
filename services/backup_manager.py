"""Safe, in-memory preparation of backups for future cleaning releases."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from core.cleaning_execution_models import CleaningOperation


@dataclass(frozen=True, slots=True)
class BackupResult:
    success: bool
    backup_id: str | None
    original_path: Path | None
    backup_path: Path | None
    message: str


class BackupManager:
    """Tracks simulated backup locations without creating, copying, or deleting files."""

    def __init__(self, backup_root: Path | None = None) -> None:
        self._backup_root = backup_root or Path("backups")
        self._records: dict[str, BackupResult] = {}

    def create_backup(self, operation: CleaningOperation) -> BackupResult:
        """Registers a future backup location without touching source or destination."""
        if not str(operation.target_path):
            return BackupResult(False, None, None, None, "Backup preparation requires a target path.")
        backup_id = str(uuid4())
        backup_path = self._backup_root / f"{backup_id}-{operation.target_path.name}.backup"
        result = BackupResult(True, backup_id, operation.target_path, backup_path, "Backup registered in safe simulation mode. No files copied.")
        self._records[backup_id] = result
        return result

    def restore_backup(self, backup_id: str) -> BackupResult:
        """Validates a record; restoration is deliberately only simulated."""
        backup = self._records.get(backup_id)
        if backup is None:
            return BackupResult(False, backup_id, None, None, "Backup record was not found.")
        return BackupResult(True, backup.backup_id, backup.original_path, backup.backup_path, "Restore validated in safe simulation mode. No files restored.")
