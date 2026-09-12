"""多显示器支持。"""
from __future__ import annotations

from typing import Optional, Tuple

from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtGui import QGuiApplication


def screen_at(pos: Tuple[int, int]) -> Optional[object]:
    """返回包含指定点（物理屏幕坐标）的屏幕对象。"""
    app = QGuiApplication.instance()
    if app is None:
        return None
    point = QPoint(int(pos[0]), int(pos[1]))
    for screen in app.screens():
        if screen.geometry().contains(point):
            return screen
    return app.primaryScreen()


def available_geometry_at(pos: Tuple[int, int]) -> QRect:
    """返回指定点所在屏幕的可用几何区域（排除任务栏）。"""
    screen = screen_at(pos)
    if screen is None:
        return QRect()
    return screen.availableGeometry()


def clamp_to_screen(x: int, y: int, width: int, height: int, offset: int = 15) -> Tuple[int, int]:
    """将窗口位置调整到光标所在屏幕内。

    默认放在光标右下方，超出屏幕右/下边缘时向左/上调整。
    """
    geometry = available_geometry_at((x, y))
    if geometry.isNull():
        return x + offset, y + offset

    px = x + offset
    py = y + offset
    if px + width > geometry.right():
        px = x - offset - width
    if py + height > geometry.bottom():
        py = y - offset - height

    # 确保不超出屏幕左/上边界
    if px < geometry.left():
        px = geometry.left() + offset
    if py < geometry.top():
        py = geometry.top() + offset
    return px, py
