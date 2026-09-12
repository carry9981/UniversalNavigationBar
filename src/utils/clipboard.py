"""剪贴板工具。"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wintypes

import pyperclip

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
GHND = 0x0042
CF_UNICODETEXT = 13


def get_clipboard_text() -> str:
    """读取剪贴板文本，失败返回空字符串。"""
    try:
        text = pyperclip.paste()
        return "" if text is None else str(text)
    except Exception:
        return ""


def set_clipboard_text(text: str) -> None:
    """写入剪贴板文本。"""
    pyperclip.copy(text)


def clipboard_has_non_text() -> bool:
    """检测剪贴板是否包含非文本数据（如图片）。"""
    try:
        if not user32.OpenClipboard(0):
            return False
        try:
            fmt = 0
            while True:
                fmt = user32.EnumClipboardFormats(fmt)
                if fmt == 0:
                    break
                if fmt != CF_UNICODETEXT and fmt != 1:  # 1 = CF_TEXT
                    return True
            return False
        finally:
            user32.CloseClipboard()
    except Exception:
        return False


def save_clipboard() -> bytes | None:
    """保存剪贴板所有内容到内存块，返回句柄数据。非文本（如图片）也能保留。"""
    try:
        if not user32.OpenClipboard(0):
            return None
        try:
            saved = []
            fmt = 0
            while True:
                fmt = user32.EnumClipboardFormats(fmt)
                if fmt == 0:
                    break
                h_data = user32.GetClipboardData(fmt)
                if h_data:
                    size = kernel32.GlobalSize(h_data)
                    if size > 0:
                        p_src = kernel32.GlobalLock(h_data)
                        if p_src:
                            data = ctypes.string_at(p_src, size)
                            kernel32.GlobalUnlock(h_data)
                            saved.append((fmt, data))
            return saved if saved else None
        finally:
            user32.CloseClipboard()
    except Exception:
        return None


def restore_clipboard(saved: list | None) -> None:
    """从 save_clipboard 返回的数据恢复剪贴板。"""
    if not saved:
        return
    try:
        if not user32.OpenClipboard(0):
            return
        try:
            user32.EmptyClipboard()
            for fmt, data in saved:
                h = kernel32.GlobalAlloc(GHND, len(data))
                if h:
                    p = kernel32.GlobalLock(h)
                    if p:
                        ctypes.memmove(p, data, len(data))
                        kernel32.GlobalUnlock(h)
                        user32.SetClipboardData(fmt, h)
        finally:
            user32.CloseClipboard()
    except Exception:
        pass
