"""触发模块：统一的全局鼠标/键盘监听与触发管理。"""
from __future__ import annotations

import threading
from typing import Optional

from .base import BaseTrigger, TriggerEvent
from .left_click_hold import LeftClickHoldTrigger
from .text_select import TextSelectTrigger

try:
    from pynput import keyboard, mouse
    _PNPUT_AVAILABLE = True
except Exception:  # pragma: no cover
    keyboard = None
    mouse = None
    _PNPUT_AVAILABLE = False

_BUTTON_MAP = {
    "left": "left",
    "right": "right",
    "middle": "middle",
}


class TriggerManager:
    """统一管理所有触发器与全局监听线程。"""

    def __init__(self, config: Optional[dict] = None, on_trigger=None, on_escape=None, on_outside_click=None) -> None:
        config = config or {}
        self.on_trigger = on_trigger
        self.on_escape = on_escape
        self.on_outside_click = on_outside_click

        self.text_select = TextSelectTrigger(config.get("text_select", {}), self._handle_trigger)
        self.left_hold = LeftClickHoldTrigger(config.get("left_click_hold", {}), self._handle_trigger)
        self.triggers: list[BaseTrigger] = [self.text_select, self.left_hold]

        self._mouse_listener = None
        self._keyboard_listener = None
        self._navbar_rect = None  # (x, y, w, h)
        self._hold_fired = False  # 本次左键按下是否已由长按触发
        self._lock = threading.Lock()

    # ------------------------------------------------------------- 回调处理
    def _handle_trigger(self, event: TriggerEvent) -> None:
        if event.source == "left_click_hold":
            # 记录长按已触发，避免同一次按压在松开时又被框选触发
            self._hold_fired = True
        if self.on_trigger is not None:
            self.on_trigger(event)

    # ------------------------------------------------------------- 外部点击
    def set_navbar_rect(self, rect) -> None:
        """设置导航条窗口几何（用于外部点击关闭）。rect: (x, y, w, h) 或 None。"""
        with self._lock:
            self._navbar_rect = rect

    def _is_inside_navbar(self, x: int, y: int) -> bool:
        with self._lock:
            rect = self._navbar_rect
        if not rect:
            return False
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    # ------------------------------------------------------------- 监听线程
    def start(self) -> None:
        if not _PNPUT_AVAILABLE:
            return
        if self._mouse_listener is None:
            self._mouse_listener = mouse.Listener(
                on_move=self._on_move,
                on_click=self._on_click,
            )
            self._mouse_listener.daemon = True
            self._mouse_listener.start()
        if self._keyboard_listener is None:
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
            )
            self._keyboard_listener.daemon = True
            self._keyboard_listener.start()

    def stop(self) -> None:
        if self._mouse_listener is not None:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._keyboard_listener is not None:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

    # ------------------------------------------------------------- pynput 事件
    def _on_move(self, x: int, y: int) -> None:
        for t in self.triggers:
            t.on_move(x, y)

    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:
        name = getattr(button, "name", None)
        if isinstance(name, str) and name in _BUTTON_MAP:
            name = _BUTTON_MAP[name]
        else:
            name = str(name)
        if name not in ("left", "right", "middle"):
            return

        navbar_visible = self._navbar_rect is not None

        # 导航条显示中，点击其外部区域时关闭（任意按键）
        if pressed and navbar_visible and not self._is_inside_navbar(x, y):
            if self.on_outside_click is not None:
                self.on_outside_click((x, y))

        if name == "left":
            if pressed:
                self._hold_fired = False
                if navbar_visible:
                    # 导航条显示时，左键用于点击条目/关闭，不启动长按触发
                    self.left_hold.reset()
                else:
                    self.left_hold.on_click(x, y, name, True)
                self.text_select.on_click(x, y, name, True)
            else:
                if self._hold_fired:
                    # 已由长按触发，取消框选触发，避免同一次操作重复/误关闭
                    self.text_select.reset()
                else:
                    self.text_select.on_click(x, y, name, False)
                self.left_hold.on_click(x, y, name, False)
            return

        # 右键/中键：仅用于外部点击关闭，不再触发导航条
        for t in self.triggers:
            t.on_click(x, y, name, pressed)

    def _on_key_press(self, key) -> None:
        try:
            if key == keyboard.Key.esc:
                if self.on_escape is not None:
                    self.on_escape()
        except Exception:
            pass


__all__ = ["BaseTrigger", "TriggerEvent", "TriggerManager", "TextSelectTrigger", "LeftClickHoldTrigger"]
