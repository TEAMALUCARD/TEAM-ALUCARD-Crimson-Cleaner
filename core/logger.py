"""
Centralized Logger Module for Crimson Cleaner.
Handles logging setup for stdout and file output under logs/crimson_cleaner.log.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(
    name: str = "CrimsonCleaner",
    log_file_dir: Path | None = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Configures and returns the central logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_file_dir is None:
        project_root = Path(__file__).resolve().parent.parent
        log_file_dir = project_root / "logs"

    try:
        log_file_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_file_dir / "crimson_cleaner.log"
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info("Logger initialized. Logs will be saved to %s", log_path)
    except Exception as e:
        logger.warning("Could not setup file logger at %s: %s", log_file_dir, e)

    return logger
