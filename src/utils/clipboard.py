"""剪贴板工具。"""
from __future__ import annotations

import time

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


def read_with_restore() -> tuple[str, str]:
    """读取剪贴板并返回 (原内容快照, 空串占位)，便于调用方恢复。"""
    return get_clipboard_text(), ""
