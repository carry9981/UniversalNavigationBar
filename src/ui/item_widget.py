"""单个条目组件。"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..config.models import Item


class ItemWidget(QFrame):
    """导航条中的单个条目，含图标与名称，可点击。"""

    clicked = pyqtSignal(object)  # 携带 Item

    # 固定条目尺寸，保证网格对齐
    ITEM_WIDTH = 90
    ITEM_HEIGHT = 70

    def __init__(self, item: Item, parent=None) -> None:
        super().__init__(parent)
        self.item = item
        self._pressed = False
        self.setObjectName("NavBarItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(self.ITEM_WIDTH, self.ITEM_HEIGHT)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_text = item.icon or "•"
        self.icon_label = QLabel(icon_text)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 22px; background: transparent; border: none;")

        self.name_label = QLabel(item.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("background: transparent; border: none;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit(self.item)
        super().mouseReleaseEvent(event)
