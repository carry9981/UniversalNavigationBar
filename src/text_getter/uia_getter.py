"""通过 Windows UI Automation 获取选中文本。"""
from __future__ import annotations

from .base import BaseTextGetter

try:
    import uiautomation as auto
    _UIA_AVAILABLE = True
except Exception:  # pragma: no cover - 非 Windows 环境
    auto = None
    _UIA_AVAILABLE = False


class UIAGetter(BaseTextGetter):
    """UI Automation 文本获取器。

    不模拟复制，不影响剪贴板，直接读取焦点元素的 TextPattern 选中范围。
    """

    name = "uiautomation"

    def is_available(self) -> bool:
        return _UIA_AVAILABLE

    def get_selected_text(self) -> str:
        if not _UIA_AVAILABLE:
            return ""
        try:
            control = auto.GetFocusedControl()
            if control is None:
                return ""
            text_pattern = control.GetPattern(auto.PatternId.TextPattern)
            if text_pattern is None:
                return ""
            ranges = text_pattern.GetSelection()
            if not ranges:
                return ""
            parts = []
            for r in ranges:
                text = r.GetText(-1)
                if text:
                    parts.append(text)
            return "".join(parts)
        except Exception:
            return ""
