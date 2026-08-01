"""
UI Package for Crimson Cleaner.
Contains main window, dashboard, theme tokens, and custom PySide6 Fluent components.
"""
from .main_window import MainWindow
from .theme import get_application_stylesheet, COLORS

__all__ = ["MainWindow", "get_application_stylesheet", "COLORS"]
