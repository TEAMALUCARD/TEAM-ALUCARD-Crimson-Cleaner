"""
Configuration Manager Service for Crimson Cleaner.
Provides a thread-safe, structured interface to manage application settings.
"""
import copy
import json
import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from typing import Any

logger = logging.getLogger("CrimsonCleaner")

DEFAULT_CONFIG: dict[str, Any] = {
    "app_name": "Crimson Cleaner",
    "team_name": "TEAM ALUCARD",
    "version": "v0.1.1 Alpha",
    "developer": "Killgore793",
    "refresh_interval_ms": 1000,
    "theme": "dark_crimson",
    "log_level": "INFO",
    "auto_start_with_windows": False,
    "minimize_to_tray": False,
    "notifications_enabled": True,
    "language": "es",
    "excluded_directories": [],
    "optimization": {
        "auto_optimize_enabled": False,
        "ram_threshold_percent": 85,
        "clean_standby_list": True,
        "clean_working_sets": True,
    },
}


class ConfigManager:
    """Manages application settings persistence and default fallbacks."""

    def __init__(self, config_path: Path | str | None = None) -> None:
        if config_path is None:
            project_root = Path(__file__).resolve().parent.parent
            self.config_path = project_root / "config" / "settings.json"
        else:
            self.config_path = Path(config_path)

        self._lock = RLock()
        self._config: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Loads configuration from JSON file or creates default configuration."""
        with self._lock:
            if not self.config_path.exists():
                logger.info("Config file not found. Creating defaults at %s", self.config_path)
                self._config = copy.deepcopy(DEFAULT_CONFIG)
                self.save()
                return

            try:
                with self.config_path.open("r", encoding="utf-8") as config_file:
                    loaded = json.load(config_file)
                if not isinstance(loaded, dict):
                    raise ValueError("The configuration root must be a JSON object.")
                self._config = self._deep_merge(DEFAULT_CONFIG, loaded)
                logger.info("Configuration loaded from %s", self.config_path)
            except (OSError, json.JSONDecodeError, ValueError) as error:
                logger.error("Unable to load configuration (%s); using defaults.", error)
                self._config = copy.deepcopy(DEFAULT_CONFIG)

    def save(self) -> bool:
        """Saves current configuration to JSON file."""
        with self._lock:
            temporary_path: Path | None = None
            try:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                with NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.config_path.parent,
                    delete=False,
                    suffix=".tmp",
                ) as temporary_file:
                    json.dump(self._config, temporary_file, indent=2, ensure_ascii=False)
                    temporary_file.flush()
                    os.fsync(temporary_file.fileno())
                    temporary_path = Path(temporary_file.name)
                os.replace(temporary_path, self.config_path)
                logger.debug("Configuration saved to %s", self.config_path)
                return True
            except OSError as error:
                logger.error("Unable to save configuration: %s", error)
                return False
            finally:
                if temporary_path is not None and temporary_path.exists():
                    temporary_path.unlink(missing_ok=True)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration value by key."""
        with self._lock:
            return copy.deepcopy(self._config.get(key, default))

    def set(self, key: str, value: Any) -> None:
        """Sets a configuration value and saves changes."""
        with self._lock:
            self._config[key] = copy.deepcopy(value)
            self.save()

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deeply merges two dictionaries."""
        result = copy.deepcopy(base)
        for k, v in override.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self._deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    @property
    def refresh_interval_ms(self) -> int:
        return int(self.get("refresh_interval_ms", 1000))

    @property
    def version(self) -> str:
        return str(self.get("version", "v0.1.1 Alpha"))

    @property
    def developer(self) -> str:
        return str(self.get("developer", "Killgore793"))

    @property
    def team_name(self) -> str:
        return str(self.get("team_name", "TEAM ALUCARD"))
