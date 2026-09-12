"""主题样式（QSS）。"""
from __future__ import annotations

from ..config.defaults import default_config

DARK_PALETTE = {
    "background": "#1E1E2E",
    "text": "#CDD6F4",
    "hover": "#313244",
    "border": "#45475A",
    "accent": "#89B4FA",
}

LIGHT_PALETTE = {
    "background": "#FFFFFF",
    "text": "#1E1E2E",
    "hover": "#E6E6F0",
    "border": "#C0C0D0",
    "accent": "#2962FF",
}


def build_stylesheet(config: dict | None = None) -> str:
    """根据配置生成全局 QSS 样式表。"""
    config = config or default_config()["ui"]
    theme = config.get("theme", "dark")
    palette = DARK_PALETTE if theme == "dark" else LIGHT_PALETTE

    radius = int(config.get("border_radius_px", 10))
    font_family = config.get("font_family", "Microsoft YaHei, sans-serif")
    font_size = int(config.get("font_size_px", 13))
    item_padding = int(config.get("item_padding_px", 8))

    bg = palette["background"]
    text = palette["text"]
    hover = palette["hover"]
    border = palette["border"]
    accent = palette["accent"]

    return f"""
    QWidget {{
        font-family: "{font_family}";
        font-size: {font_size}px;
        color: {text};
    }}
    #NavBarContainer {{
        background-color: {bg};
        border: 1px solid {border};
        border-radius: {radius}px;
    }}
    #NavBarHeader {{
        color: {text};
        background: transparent;
    }}
    #NavBarCloseButton {{
        color: {text};
        background: transparent;
        border: none;
        font-size: {font_size}px;
        padding: 2px 6px;
    }}
    #NavBarCloseButton:hover {{
        color: {accent};
        background: {hover};
        border-radius: {radius}px;
    }}
    #NavBarItem {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: {radius // 2}px;
        padding: {item_padding}px {item_padding + 4}px;
        color: {text};
    }}
    #NavBarItem:hover {{
        background-color: {hover};
        border: 1px solid {border};
    }}
    QDialog, QMainWindow {{
        background-color: {bg};
    }}
    QPushButton {{
        background-color: {hover};
        border: 1px solid {border};
        border-radius: {radius // 2}px;
        padding: 6px 12px;
        color: {text};
    }}
    QPushButton:hover {{
        background-color: {accent};
        color: #11111b;
    }}
    QLineEdit, QTextEdit, QSpinBox, QComboBox {{
        background-color: {hover};
        border: 1px solid {border};
        border-radius: {radius // 2}px;
        padding: 4px 6px;
        color: {text};
    }}
    QListWidget {{
        background-color: {bg};
        border: 1px solid {border};
        border-radius: {radius // 2}px;
    }}
    QListWidget::item:selected {{
        background-color: {hover};
    }}
    QCheckBox {{
        spacing: 6px;
    }}
    QLabel {{
        background: transparent;
    }}
    """
