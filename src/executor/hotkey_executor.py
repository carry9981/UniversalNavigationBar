"""快捷键执行器。"""
from __future__ import annotations

import time

from .base import BaseExecutor

try:
    from pynput.keyboard import Controller, Key, KeyCode
    _AVAILABLE = True
except Exception:  # pragma: no cover
    Controller = None
    Key = None
    KeyCode = None
    _AVAILABLE = False

from ..config.models import ConfigError, Context, Item

_MODIFIERS = {
    "ctrl": Key.ctrl if Key else None,
    "control": Key.ctrl if Key else None,
    "alt": Key.alt if Key else None,
    "shift": Key.shift if Key else None,
    "win": Key.cmd if Key else None,
    "cmd": Key.cmd if Key else None,
    "super": Key.cmd if Key else None,
}

_SPECIALS = {
    "enter": Key.enter,
    "return": Key.enter,
    "space": Key.space,
    "tab": Key.tab,
    "escape": Key.esc,
    "esc": Key.esc,
    "backspace": Key.backspace,
    "delete": Key.delete,
    "del": Key.delete,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
    "home": Key.home,
    "end": Key.end,
    "pageup": Key.page_up,
    "pagedown": Key.page_down,
    "insert": Key.insert,
    "capslock": Key.caps_lock,
}


def resolve_key(name: str):
    """将按键名解析为 pynput 键对象。"""
    if not _AVAILABLE:
        return None
    n = str(name).lower().strip()
    if n in _MODIFIERS:
        return _MODIFIERS[n]
    if n in _SPECIALS:
        return _SPECIALS[n]
    if n.startswith("f") and n[1:].isdigit() and 1 <= int(n[1:]) <= 12:
        return getattr(Key, n, None)
    if len(n) == 1:
        return KeyCode.from_char(n)
    return None


class HotkeyExecutor(BaseExecutor):
    """模拟键盘快捷键。"""

    def is_available(self) -> bool:
        return _AVAILABLE

    def run(self, item: Item, context: Context) -> None:
        if not _AVAILABLE:
            return
        keys = item.config.get("keys", [])
        delay = float(item.config.get("delay_ms", 50)) / 1000.0

        resolved = []
        for name in keys:
            key = resolve_key(name)
            if key is None:
                raise ConfigError(f"无法识别的按键名: {name}")
            resolved.append(key)

        controller = Controller()
        for key in resolved:
            controller.press(key)
            if delay:
                time.sleep(delay)
        for key in reversed(resolved):
            controller.release(key)
            if delay:
                time.sleep(delay)
