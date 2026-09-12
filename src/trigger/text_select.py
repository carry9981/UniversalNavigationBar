"""框选文本触发。"""
from __future__ import annotations

import math
import time
from typing import Optional

from .base import BaseTrigger


class TextSelectTrigger(BaseTrigger):
    """监听鼠标左键按下→移动→释放，判定为框选后触发。"""

    source = "text_select"

    def __init__(self, config: Optional[dict] = None, on_trigger=None) -> None:
        super().__init__(config, on_trigger)
        self.min_distance = float(self.config.get("min_distance_px", 15))
        self.max_duration = float(self.config.get("max_duration_sec", 2.0))
        self._start_x: Optional[int] = None
        self._start_y: Optional[int] = None
        self._start_time: Optional[float] = None
        self._dragging = False

    def on_move(self, x: int, y: int) -> None:
        if self._start_x is not None and not self._dragging:
            # 只有移动超过最小距离才认为开始框选
            if math.hypot(x - self._start_x, y - self._start_y) >= self.min_distance:
                self._dragging = True

    def on_click(self, x: int, y: int, button: str, pressed: bool) -> None:
        if not self.enabled:
            return
        if button != "left":
            return
        if pressed:
            self._start_x = x
            self._start_y = y
            self._start_time = time.monotonic()
            self._dragging = False
            return
        # 左键释放
        if self._start_x is None or self._start_time is None:
            return
        end_x, end_y = x, y
        start_x, start_y = self._start_x, self._start_y
        duration = time.monotonic() - self._start_time
        self.reset()

        distance = math.hypot(end_x - start_x, end_y - start_y)
        if distance < self.min_distance:
            return
        if duration > self.max_duration:
            return
        self._fire(end_x, end_y)

    def reset(self) -> None:
        self._start_x = None
        self._start_y = None
        self._start_time = None
        self._dragging = False
