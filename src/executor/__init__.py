"""动作执行模块。"""
from __future__ import annotations

from typing import Optional

from .base import BaseExecutor
from .click_executor import ClickExecutor
from .hotkey_executor import HotkeyExecutor
from .script_executor import ScriptExecutor
from .text_executor import TextExecutor

from ..config.models import ConfigError, Context, Item


class ActionExecutor:
    """动作执行引擎：根据条目类型分发到对应执行器。"""

    def __init__(self, plugin_dir: Optional[str] = None) -> None:
        self.hotkey = HotkeyExecutor()
        self.text = TextExecutor()
        self.script = ScriptExecutor(plugin_dir=plugin_dir)
        self.click = ClickExecutor()

    def execute(self, item: Item, context: Context) -> None:
        """执行单个条目动作。"""
        executor = self._resolve(item)
        if executor is None:
            raise ConfigError(f"未知的条目类型: {item.type}")
        executor.run(item, context)

    def _resolve(self, item: Item) -> Optional[BaseExecutor]:
        if item.type == "hotkey":
            return self.hotkey
        if item.type == "text":
            return self.text
        if item.type == "script":
            return self.script
        if item.type == "click_sequence":
            return self.click
        return None


__all__ = [
    "ActionExecutor",
    "BaseExecutor",
    "ClickExecutor",
    "HotkeyExecutor",
    "ScriptExecutor",
    "TextExecutor",
]
