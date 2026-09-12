"""开机自启动（Windows 注册表）。"""
from __future__ import annotations

import os
import sys

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "UniversalNavBar"


def _command() -> str:
    """返回启动命令。打包后为 exe 路径，开发环境为 pythonw + main.py。"""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    main_py = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py"))
    return f'"{pythonw}" "{main_py}"'


def _open_key():
    import winreg

    return winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)


def is_enabled() -> bool:
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            try:
                winreg.QueryValueEx(key, VALUE_NAME)
                return True
            except FileNotFoundError:
                return False
    except Exception:
        return False


def set_enabled(enabled: bool) -> bool:
    """启用/禁用开机自启动，返回是否成功。"""
    try:
        import winreg

        with _open_key() as key:
            if enabled:
                winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, _command())
            else:
                try:
                    winreg.DeleteValue(key, VALUE_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception as exc:
        print(f"[autostart] 设置开机自启动失败: {exc}")
        return False
