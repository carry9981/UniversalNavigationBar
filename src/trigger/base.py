"""触发器基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class TriggerEvent:
    """触发事件。"""

    def __init__(self, x: int, y: int, source: str) -> None:
        self.x = x
        self.y = y
        self.source = source


class BaseTrigger(ABC):
    """全局鼠标事件触发器基类。"""

    source = "base"

    def __init__(self, config: Optional[dict] = None, on_trigger=None) -> None:
        self.config = config or {}
        self.on_trigger = on_trigger
        self.enabled = bool(self.config.get("enabled", True))

    @abstractmethod
    def on_move(self, x: int, y: int) -> None:
        """鼠标移动。"""

    @abstractmethod
    def on_click(self, x: int, y: int, button: str, pressed: bool) -> None:
        """鼠标按键。button: 'left' | 'right' | 'middle'。"""

    def reset(self) -> None:
        """重置内部状态。"""

    def _fire(self, x: int, y: int) -> None:
        if self.on_trigger is not None:
            self.on_trigger(TriggerEvent(x, y, self.source))
