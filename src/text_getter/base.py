"""文本获取器基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTextGetter(ABC):
    """获取选中文本的抽象基类。"""

    name = "base"

    @abstractmethod
    def get_selected_text(self) -> str:
        """返回当前选中文本；失败返回空字符串。"""
        raise NotImplementedError
