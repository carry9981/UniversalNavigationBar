"""文本获取模块：门面模式，支持 UIA 主方案与剪贴板降级。"""
from __future__ import annotations

import time
from typing import Optional

from .base import BaseTextGetter
from .clipboard_getter import ClipboardGetter
from .uia_getter import UIAGetter


class TextGetter:
    """组合获取器，按配置选择主方案并在失败时降级。"""

    def __init__(self, config: Optional[dict] = None) -> None:
        config = config or {}
        self.method = config.get("method", "uiautomation")
        self.fallback_to_clipboard = bool(config.get("fallback_to_clipboard", True))
        self.clipboard_restore = bool(config.get("clipboard_restore", True))
        self.cache_duration_ms = int(config.get("cache_duration_ms", 500))

        self._uia = UIAGetter()
        self._clipboard = ClipboardGetter(restore=self.clipboard_restore)
        self._cache_text: str = ""
        self._cache_time: float = 0.0

    def get_selected_text(self) -> str:
        """获取选中文本；带缓存，失败时降级到剪贴板。"""
        now = time.monotonic()
        if now - self._cache_time < self.cache_duration_ms / 1000.0:
            return self._cache_text

        text = ""
        if self.method == "uiautomation" and self._uia.is_available():
            text = self._uia.get_selected_text()

        if not text and self.method == "clipboard" and self._clipboard.is_available():
            text = self._clipboard.get_selected_text()
        elif not text and self.fallback_to_clipboard and self._clipboard.is_available():
            text = self._clipboard.get_selected_text()

        self._cache_text = text
        self._cache_time = now
        return text

    def invalidate_cache(self) -> None:
        self._cache_time = 0.0


__all__ = ["BaseTextGetter", "ClipboardGetter", "UIAGetter", "TextGetter"]
