"""剪贴板工具。"""
from __future__ import annotations

import pyperclip


def get_clipboard_text() -> str:
    """读取剪贴板文本，失败返回空字符串。"""
    try:
        text = pyperclip.paste()
        return "" if text is None else str(text)
    except Exception:
        return ""


def set_clipboard_text(text: str) -> None:
    """写入剪贴板文本。"""
    pyperclip.copy(text)
