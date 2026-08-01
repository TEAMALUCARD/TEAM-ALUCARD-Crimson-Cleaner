"""
Main Entry Point for Crimson Cleaner | TEAM ALUCARD.
Version: v0.1.1 Alpha
Dev: Killgore793
"""
import sys
import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from app import CrimsonCleanerApp


def excepthook(exc_type, exc_value, exc_traceback):
    """Global unhandled exception logger hook."""
    logger = logging.getLogger("CrimsonCleaner")
    logger.critical("Unhandled exception encountered:", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main() -> None:
    """Main execution function."""
    sys.excepthook = excepthook

    # High-DPI Scaling Policy
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = CrimsonCleanerApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
