"""预设文本输入执行器。"""
from __future__ import annotations

import time

from .base import BaseExecutor

try:
    from pynput.keyboard import Controller, Key
    _AVAILABLE = True
except Exception:  # pragma: no cover
    Controller = None
    Key = None
    _AVAILABLE = False

from ..config.models import Context, Item
from ..utils.clipboard import get_clipboard_text, set_clipboard_text, save_clipboard, restore_clipboard
from ..utils.variables import replace_variables


class TextExecutor(BaseExecutor):
    """输入预设文本（type 逐字符 / paste 剪贴板粘贴）。"""

    def is_available(self) -> bool:
        return _AVAILABLE

    def run(self, item: Item, context: Context) -> None:
        if not _AVAILABLE:
            return
        config = item.config
        content = config.get("content", "")
        mode = config.get("mode", "type")
        delay_ms = int(config.get("delay_ms", 10))
        variables_enabled = bool(config.get("variables", True))

        text = replace_variables(content, context.as_mapping(), variables_enabled)
        if not text:
            return

        if mode == "paste":
            self._paste(text)
        else:
            self._type(text, delay_ms)

    def _paste(self, text: str) -> None:
        saved = save_clipboard()
        try:
            set_clipboard_text(text)
            keyboard = Controller()
            with keyboard.pressed(Key.ctrl):
                keyboard.press("v")
                keyboard.release("v")
        finally:
            if saved:
                restore_clipboard(saved)

    def _type(self, text: str, delay_ms: int) -> None:
        keyboard = Controller()
        if delay_ms <= 0:
            keyboard.type(text)
            return
        for ch in text:
            keyboard.type(ch)
            time.sleep(delay_ms / 1000.0)
