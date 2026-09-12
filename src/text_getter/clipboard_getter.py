"""剪贴板降级文本获取器。

通过模拟 Ctrl+C 获取选中文本，并在读取后恢复原剪贴板内容。
"""
from __future__ import annotations

import time

from .base import BaseTextGetter

try:
    from pynput.keyboard import Controller, Key
    _KEYBOARD_AVAILABLE = True
except Exception:  # pragma: no cover
    Controller = None
    Key = None
    _KEYBOARD_AVAILABLE = False

from ..utils.clipboard import get_clipboard_text, save_clipboard, restore_clipboard


class ClipboardGetter(BaseTextGetter):
    """剪贴板方式获取选中文本（降级方案）。"""

    name = "clipboard"

    def __init__(self, restore: bool = True, wait_ms: int = 100) -> None:
        self.restore = restore
        self.wait_ms = wait_ms

    def is_available(self) -> bool:
        return _KEYBOARD_AVAILABLE

    def get_selected_text(self) -> str:
        if not _KEYBOARD_AVAILABLE:
            return ""
        saved = save_clipboard() if self.restore else None
        try:
            keyboard = Controller()
            with keyboard.pressed(Key.ctrl):
                keyboard.press("c")
                keyboard.release("c")
            time.sleep(self.wait_ms / 1000.0)
            return get_clipboard_text()
        except Exception:
            return ""
        finally:
            if self.restore and saved:
                restore_clipboard(saved)
