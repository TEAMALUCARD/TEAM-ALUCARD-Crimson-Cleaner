"""
Theme and Design Tokens for Crimson Cleaner.
Defines color palette constants and Fluent Dark PySide6 QSS stylesheet.
"""
from typing import Dict

# Design Tokens (Color Palette)
COLORS: Dict[str, str] = {
    "bg_root": "#0C0C0F",
    "bg_card": "#14141A",
    "bg_card_hover": "#1A1A22",
    "bg_input": "#181820",
    "border": "#282834",
    "border_light": "#383848",
    "primary": "#DC143C",          # Crimson
    "primary_hover": "#FF2E55",    # Bright Crimson Glow
    "primary_pressed": "#B00C2E",  # Dark Crimson
    "accent_gold": "#FFD700",
    "text_main": "#F3F3F6",
    "text_secondary": "#9E9EA8",
    "text_muted": "#6C6C78",
    "success": "#20C997",
    "warning": "#FFC107",
    "danger": "#FF4D4D",
}


def get_application_stylesheet() -> str:
    """Returns the main Qt QSS stylesheet for the application."""
    return f"""
    /* Global Application Theme */
    QWidget {{
        background-color: {COLORS['bg_root']};
        color: {COLORS['text_main']};
        font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
        font-size: 13px;
    }}

    QMainWindow {{
        background-color: {COLORS['bg_root']};
    }}

    /* Card Containers */
    QFrame#StatCard, QFrame#DashboardCard, QFrame#LogCard {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
    }}

    QFrame#StatCard:hover {{
        border: 1px solid {COLORS['border_light']};
        background-color: {COLORS['bg_card_hover']};
    }}

    /* Labels */
    QLabel {{
        background: transparent;
    }}

    QLabel#TitleLabel {{
        font-size: 16px;
        font-weight: 700;
        color: {COLORS['text_main']};
    }}

    QLabel#SubTitleLabel {{
        font-size: 12px;
        color: {COLORS['text_secondary']};
    }}

    QLabel#ValueLabel {{
        font-size: 22px;
        font-weight: bold;
        color: {COLORS['text_main']};
    }}

    QLabel#BadgeLabel {{
        background-color: rgba(220, 20, 60, 0.18);
        color: {COLORS['primary_hover']};
        border: 1px solid rgba(220, 20, 60, 0.4);
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 11px;
        font-weight: 600;
    }}

    QLabel#DevBadgeLabel {{
        background-color: rgba(255, 215, 0, 0.12);
        color: {COLORS['accent_gold']};
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 11px;
        font-weight: 600;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        border: none;
        background: {COLORS['bg_root']};
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical {{
        background: {COLORS['border_light']};
        min-height: 20px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {COLORS['primary']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Text Edit / Log Console */
    QTextEdit#LogConsole {{
        background-color: {COLORS['bg_input']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
        color: {COLORS['text_main']};
    }}
    """
