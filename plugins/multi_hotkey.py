#!/usr/bin/env python3
"""
UNB 插件：连续执行多个快捷键
args 参数格式：每组快捷键用逗号分隔，多组用分号分隔
示例：["ctrl+a", "ctrl+c"] 会先执行全选，再执行复制
"""

import sys
import time

try:
    from pynput.keyboard import Controller, Key, KeyCode
except ImportError:
    print("pynput 未安装")
    sys.exit(1)

_MODIFIERS = {
    "ctrl": Key.ctrl,
    "control": Key.ctrl,
    "alt": Key.alt,
    "shift": Key.shift,
    "win": Key.cmd,
    "cmd": Key.cmd,
    "super": Key.cmd,
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


def resolve_key(name):
    n = name.lower().strip()
    if n in _MODIFIERS:
        return _MODIFIERS[n]
    if n in _SPECIALS:
        return _SPECIALS[n]
    if n.startswith("f") and n[1:].isdigit() and 1 <= int(n[1:]) <= 12:
        return getattr(Key, n, None)
    if len(n) == 1:
        return KeyCode.from_char(n)
    return None


def run_hotkey(combo_str, controller, delay):
    """执行单个快捷键组合，如 'ctrl+c'"""
    parts = [p.strip() for p in combo_str.split("+") if p.strip()]
    keys = []
    for part in parts:
        key = resolve_key(part)
        if key is None:
            print(f"无法识别的按键: {part}")
            return
        keys.append(key)

    for key in keys:
        controller.press(key)
        time.sleep(delay)
    for key in reversed(keys):
        controller.release(key)
        time.sleep(delay)


def main():
    # 从命令行参数获取快捷键组合
    if len(sys.argv) < 2:
        print("用法: multi_hotkey.py <combo1> [combo2] ...")
        print("示例: multi_hotkey.py ctrl+a ctrl+c")
        sys.exit(1)

    combos = sys.argv[1:]
    controller = Controller()
    delay = 0.05  # 50ms

    for combo in combos:
        run_hotkey(combo, controller, delay)
        time.sleep(0.1)  # 组合之间间隔 100ms


if __name__ == "__main__":
    main()
