"""左键长按触发。"""
from __future__ import annotations

import math
import threading
from typing import Optional

from .base import BaseTrigger


class LeftClickHoldTrigger(BaseTrigger):
    """监听鼠标左键长按：按住达到阈值且未拖动时触发。

    若按住过程中拖动（超过 move_tolerance_px），则视为普通拖拽，不触发。
    这样不影响鼠标左键原有的点击与拖拽功能。
    """

    source = "left_click_hold"

    def __init__(self, config: Optional[dict] = None, on_trigger=None) -> None:
        super().__init__(config, on_trigger)
        self.hold_duration = float(self.config.get("hold_duration_sec", 0.5))
        self.move_tolerance = float(self.config.get("move_tolerance_px", 6))
        self._pressed = False
        self._moved = False
        self._start = (0, 0)
        self._timer: Optional[threading.Timer] = None

    def on_move(self, x: int, y: int) -> None:
        if not self._pressed:
            return
        if math.hypot(x - self._start[0], y - self._start[1]) > self.move_tolerance:
            # 发生拖动：取消长按，不触发
            self._moved = True
            self._cancel_timer()

    def on_click(self, x: int, y: int, button: str, pressed: bool) -> None:
        if not self.enabled or button != "left":
            return
        if pressed:
            self._pressed = True
            self._moved = False
            self._start = (x, y)
            self._cancel_timer()
            self._timer = threading.Timer(self.hold_duration, self._fire_if_held, args=(x, y))
            self._timer.daemon = True
            self._timer.start()
        else:
            self._pressed = False
            self._cancel_timer()

    def _fire_if_held(self, x: int, y: int) -> None:
        if self._pressed and not self._moved:
            self._fire(x, y)

    def _cancel_timer(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def reset(self) -> None:
        self._pressed = False
        self._moved = False
        self._cancel_timer()
