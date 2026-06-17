"""暗色低奢主題 — 鐵黑 · 金 · 白"""

# ── Backgrounds ──────────────────────────────
BG          = "#1C1C1E"
SURFACE     = "#2C2C2E"
SURFACE_ALT = "#3A3A3C"

# ── Text ─────────────────────────────────────
TEXT        = "#F2F2F7"
TEXT_SUB    = "#8E8E93"
TEXT_MUTED  = "#636366"

# ── Borders ──────────────────────────────────
BORDER      = "#3A3A3C"
BORDER_STR  = "#48484A"

# ── Accent ───────────────────────────────────
ACCENT_GOLD = "#C9A84C"

# ── Semantic greens / action ──────────────────
GREEN       = "#3E8B5E"
GREEN_DARK  = "#316D4A"
GREEN_LIGHT = "#1A3828"   # selection bg

BLUE        = "#0A84FF"
BLUE_DARK   = "#0870D4"
RED         = "#FF453A"
RED_DARK    = "#D93A30"
ORANGE      = "#FF9F0A"

# ── Semantic status ───────────────────────────
OVERDUE_BG  = "#3D1A1A"
STATS_BG    = "#2C2C2E"


# ── Button helpers ────────────────────────────
def btn_primary(color: str = GREEN) -> str:
    return (
        f"background:{color};color:#FFFFFF;font-weight:bold;"
        f"padding:8px 24px;border-radius:6px;border:none;"
    )


def btn_small(color: str = GREEN) -> str:
    return (
        f"background:{color};color:#FFFFFF;font-weight:bold;"
        f"padding:6px 14px;border-radius:6px;border:none;"
    )


def btn_rating(color: str) -> str:
    return (
        f"background:{color};color:#FFFFFF;font-weight:bold;"
        f"padding:10px 8px;border-radius:6px;font-size:13px;border:none;"
    )


def btn_swatch(color: str) -> str:
    return f"background:{color};border:1px solid {BORDER};border-radius:2px;"


# ── Global QSS ───────────────────────────────
STYLESHEET = f"""
QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: "PingFang TC", "Hiragino Sans", "Noto Sans CJK TC", sans-serif;
    font-size: 13px;
}}
QMainWindow, QDialog {{
    background: {BG};
}}

/* ── Tabs ─────────────────────────── */
QTabWidget::pane {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
}}
QTabBar::tab {{
    background: {SURFACE};
    color: {TEXT_SUB};
    padding: 8px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {ACCENT_GOLD};
    border-bottom: 2px solid {ACCENT_GOLD};
}}
QTabBar::tab:hover:!selected {{
    color: {TEXT};
    background: {SURFACE_ALT};
}}

/* ── Buttons ──────────────────────── */
QPushButton {{
    background: {SURFACE_ALT};
    color: {TEXT};
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
}}
QPushButton:hover {{
    background: {BORDER_STR};
}}
QPushButton:pressed {{
    background: {ACCENT_GOLD};
    color: {BG};
}}
QPushButton:disabled {{
    color: {TEXT_MUTED};
}}

/* ── Inputs ───────────────────────── */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit {{
    background: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    selection-background-color: {GREEN_LIGHT};
    selection-color: {TEXT};
}}
QLineEdit:focus, QDateEdit:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QTextEdit:focus {{
    border-color: {ACCENT_GOLD};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    selection-background-color: {GREEN_LIGHT};
    selection-color: {TEXT};
    outline: none;
}}

/* ── Table ────────────────────────── */
QTableWidget {{
    background-color: {SURFACE};
    gridline-color: {BORDER};
    color: {TEXT};
    border: 1px solid {BORDER};
    outline: none;
}}
QTableWidget::item:selected {{
    background: {GREEN_LIGHT};
    color: {TEXT};
}}
QHeaderView::section {{
    background-color: {SURFACE_ALT};
    color: {TEXT_SUB};
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER_STR};
    padding: 6px 8px;
    font-weight: bold;
    font-size: 12px;
}}

/* ── List ─────────────────────────── */
QListWidget {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    color: {TEXT};
    outline: none;
}}
QListWidget::item {{
    padding: 4px 6px;
}}
QListWidget::item:selected {{
    background: {GREEN_LIGHT};
    color: {TEXT};
}}
QListWidget::item:hover:!selected {{
    background: {SURFACE_ALT};
}}

/* ── GroupBox ─────────────────────── */
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    margin-top: 14px;
    padding-top: 6px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background: {BG};
    font-weight: bold;
    color: {TEXT_SUB};
}}

/* ── ScrollBar ────────────────────── */
QScrollBar:vertical {{
    background: {SURFACE};
    width: 8px;
    border: none;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_STR};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {SURFACE};
    height: 8px;
    border: none;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER_STR};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Calendar ─────────────────────── */
QCalendarWidget QAbstractItemView {{
    background: {SURFACE};
    selection-background-color: {ACCENT_GOLD};
    selection-color: {BG};
}}
"""
