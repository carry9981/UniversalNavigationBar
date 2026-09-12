"""点击序列执行器（预留，后期实现）。"""
from __future__ import annotations

from .base import BaseExecutor
from ..config.models import Context, Item


class ClickExecutor(BaseExecutor):
    """执行鼠标点击序列（后期版本实现）。"""

    def run(self, item: Item, context: Context) -> None:
        raise NotImplementedError("click_sequence 类型将在后续版本支持")
