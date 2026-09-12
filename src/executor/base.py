"""执行器基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..config.models import Context, Item


class BaseExecutor(ABC):
    """动作执行器抽象基类。"""

    @abstractmethod
    def run(self, item: Item, context: Context) -> None:
        """执行条目动作。"""
        raise NotImplementedError
