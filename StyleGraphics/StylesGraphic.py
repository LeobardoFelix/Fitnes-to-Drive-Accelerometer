
# ── Paleta global ────────────────────────────────────────────────────────────
DARK_BG      = "#0D0F14"
PANEL_BG     = "#141720"
BORDER       = "#252A38"
ACCENT_CYAN  = "#00E5C8"
ACCENT_RED   = "#FF4C6A"
ACCENT_AMBER = "#FFB830"
ACCENT_BLUE  = "#4C8EFF"
ACCENT_YELLOW = "#F3FF0B"
ACCENT_GREEN = "#0BFF1B"
TEXT_PRIMARY = "#E8EAF0"
TEXT_MUTED   = "#6B7280"
TEXT_LABEL   = "#9CA3AF"

STYLE_SHEET = f"""
QMainWindow, QDialog, QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 12px;
}}

/* ── Inputs ──────────────────────── */
QLineEdit {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    color: {TEXT_PRIMARY};
    padding: 4px 8px;
    selection-background-color: {ACCENT_CYAN};
    selection-color: {DARK_BG};
}}
QLineEdit:focus {{
    border-color: {ACCENT_CYAN};
}}

/* ── Botones ─────────────────────── */
QPushButton {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    color: {TEXT_PRIMARY};
    padding: 5px 14px;
    min-width: 80px;
}}
QPushButton:hover {{
    border-color: {ACCENT_CYAN};
    color: {ACCENT_CYAN};
}}
QPushButton:pressed {{
    background-color: {BORDER};
}}
QPushButton#btnEnviar {{
    border-color: {ACCENT_CYAN};
    color: {ACCENT_CYAN};
    font-weight: bold;
}}
QPushButton#btnConectar {{
    border-color: {ACCENT_CYAN};
    color: {ACCENT_CYAN};
    font-weight: bold;
    min-width: 140px;
    padding: 8px 20px;
}}
QPushButton#btnStart {{
    border-color: #3DDC84;
    color: #3DDC84;
}}
QPushButton#btnStop {{
    border-color: {ACCENT_RED};
    color: {ACCENT_RED};
}}
QPushButton#btnReconectar {{
    border-color: {ACCENT_AMBER};
    color: {ACCENT_AMBER};
}}

/* ── Labels ──────────────────────── */
QLabel {{
    color: {TEXT_LABEL};
}}
QLabel#labelTitle {{
    color: {ACCENT_CYAN};
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 3px;
}}
QLabel#labelSubtitle {{
    color: {TEXT_MUTED};
    font-size: 10px;
    letter-spacing: 2px;
}}
QLabel#labelPromedio {{
    color: {ACCENT_CYAN};
    font-size: 13px;
    font-weight: bold;
}}
QLabel#labelStatus {{
    color: {TEXT_MUTED};
    font-size: 10px;
}}

/* ── CheckBox ────────────────────── */
QCheckBox {{
    color: {TEXT_LABEL};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background-color: {PANEL_BG};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT_CYAN};
    border-color: {ACCENT_CYAN};
}}

/* ── Slider ──────────────────────── */
QSlider::groove:horizontal {{
    height: 4px;
    background: {BORDER};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT_CYAN};
    border: none;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT_CYAN};
    border-radius: 2px;
}}

/* ── GroupBox ────────────────────── */
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 18px;
    padding-top: 6px;
    color: {TEXT_MUTED};
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    top: 4px;
}}

/* ── Log ─────────────────────────── */
QTextEdit {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    color: #7CFFD4;
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 11px;
    selection-background-color: {ACCENT_CYAN};
    selection-color: {DARK_BG};
}}

/* ── Scrollbar ───────────────────── */
QScrollBar:vertical {{
    background: {PANEL_BG};
    width: 6px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 20px;
}}

/* ── Separadores ─────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {BORDER};
}}
"""
