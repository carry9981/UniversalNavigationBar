"""导航条窗口。"""
from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QRect, QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..config.defaults import APP_DISPLAY_NAME
from ..config.models import Item
from .item_widget import ItemWidget
from .multi_monitor import clamp_to_screen

# 布局常量：容器外边距 + 头部行高度 + 间距（垂直“chrome”）
_H_MARGIN = 24  # 左右各 12
_V_TOP = 8
_HEADER_H = 26
_SPACING = 6
_V_BOTTOM = 10
_V_CHROME = _V_TOP + _HEADER_H + _SPACING + _V_BOTTOM  # 内容区外的垂直占用
_SCROLLBAR_W = 17


class FlowLayout(QLayout):
    """自动换行的流式布局。"""

    def __init__(self, parent=None, margin: int = 0, spacing: int = 4) -> None:
        super().__init__(parent)
        self._items: list = []
        self._margin = margin
        self._spacing = spacing
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item) -> None:  # noqa: N802
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):  # noqa: N802
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int):  # noqa: N802
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):  # noqa: N802
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect: QRect) -> None:  # noqa: N802
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self) -> QSize:  # noqa: N802
        return self.minimumSize()

    def minimumSize(self) -> QSize:  # noqa: N802
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        x = rect.x() + self._margin
        y = rect.y() + self._margin
        line_height = 0
        effective_width = rect.width() - 2 * self._margin
        line_items = []
        for item in self._items:
            widget = item.widget()
            if widget is None:
                continue
            hint = item.sizeHint()
            w = hint.width()
            h = hint.height()
            if x + w > rect.x() + effective_width and line_height > 0:
                if not test_only:
                    self._place_line(line_items, rect.x() + self._margin, y, line_height, effective_width)
                y += line_height + self._spacing
                line_height = 0
                line_items = []
                x = rect.x() + self._margin
            line_items.append((item, x, y, w, h))
            x += w + self._spacing
            line_height = max(line_height, h)
        if line_items:
            if not test_only:
                self._place_line(line_items, rect.x() + self._margin, y, line_height, effective_width)
            y += line_height
        return y - rect.y() + self._margin

    def _place_line(self, line_items, line_x, line_y, line_height, available_width):
        line_width = sum(item[3] for item in line_items) + self._spacing * (len(line_items) - 1)
        offset_x = max(0, (available_width - line_width) // 2)
        x = line_x + offset_x
        for item, _, _, w, h in line_items:
            item.setGeometry(QRect(x, line_y, w, h))
            x += w + self._spacing


class NavBar(QWidget):
    """无边框、置顶、不抢占焦点的导航条窗口。"""

    item_clicked = pyqtSignal(object)  # 携带 Item

    def __init__(self, ui_config: Optional[dict] = None, stylesheet: str = "") -> None:
        super().__init__()
        self.ui_config = ui_config or {}
        self._stylesheet = stylesheet

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowOpacity(float(self.ui_config.get("opacity", 0.92)))

        self._build_ui()
        self.hide()

    # ------------------------------------------------------------- UI 构建
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.container = QFrame()
        self.container.setObjectName("NavBarContainer")

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(_H_MARGIN // 2, _V_TOP, _H_MARGIN // 2, _V_BOTTOM)
        container_layout.setSpacing(_SPACING)

        # 头部
        header = QHBoxLayout()
        title = QLabel(f"🧭 {APP_DISPLAY_NAME}")
        title.setObjectName("NavBarHeader")
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("NavBarCloseButton")
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setFixedSize(24, 24)
        self.close_button.clicked.connect(self.hide_navbar)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.close_button)
        container_layout.addLayout(header)

        # 条目流式布局
        self.items_container = QWidget()
        self.items_container.setStyleSheet("background: transparent; border: none;")
        self.flow = FlowLayout(self.items_container, margin=0, spacing=6)

        # 滚动区域（条目过多时）
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(False)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setMinimumHeight(0)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.scroll.setWidget(self.items_container)
        container_layout.addWidget(self.scroll)

        if self.ui_config.get("shadow", True):
            shadow = QGraphicsDropShadowEffect(self.container)
            shadow.setBlurRadius(20)
            shadow.setOffset(0, 2)
            shadow.setColor(Qt.GlobalColor.black)
            self.container.setGraphicsEffect(shadow)

        outer.addWidget(self.container)
        self.setStyleSheet(self._stylesheet)

    # ------------------------------------------------------------- 显示/隐藏
    def show_items(self, items: List[Item], pos) -> None:
        """渲染条目并显示在光标附近。"""
        self._rebuild_items(items)
        self.scroll.verticalScrollBar().setValue(0)

        offset = int(self.ui_config.get("position_offset_px", 15))
        max_width = int(self.ui_config.get("max_width_px", 400))
        max_height = int(self.ui_config.get("max_height_px", 520))

        width = min(self._desired_width(), max_width)
        inner_width = width - _H_MARGIN

        # 先重置容器尺寸，让 FlowLayout 能正确计算布局
        self.items_container.setFixedSize(inner_width, 0)
        self.scroll.setFixedHeight(max_height)

        # 内容自然高度
        content_h = self.flow.heightForWidth(inner_width)
        natural_h = content_h + _V_CHROME

        if natural_h <= max_height:
            # 无需滚动：内容贴合
            container_w, container_h = inner_width, content_h
            scroll_h = content_h
            outer_h = natural_h
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            # 内容超高：预留滚动条宽度，限制整体高度并滚动
            inner_width = inner_width - _SCROLLBAR_W
            self.items_container.setFixedSize(inner_width, 0)
            content_h = self.flow.heightForWidth(inner_width)
            container_w, container_h = inner_width, content_h
            scroll_h = max_height - (_V_TOP + _HEADER_H + _SPACING + _V_BOTTOM)
            outer_h = max_height
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.items_container.setFixedSize(container_w, container_h)
        self.scroll.setFixedHeight(scroll_h)
        self.setFixedWidth(width)
        self.setFixedHeight(outer_h)

        x, y = clamp_to_screen(int(pos[0]), int(pos[1]), self.width(), self.height(), offset)
        self.move(x, y)
        self.show()
        self.raise_()

    def _desired_width(self) -> int:
        """根据条目内容计算合适的宽度（不超 max_width）。"""
        max_width = int(self.ui_config.get("max_width_px", 400))
        item_w = ItemWidget.ITEM_WIDTH + self.flow.spacing()
        cols = max(1, (max_width - _H_MARGIN + self.flow.spacing()) // item_w)
        return min(cols * item_w + _H_MARGIN, max_width)

    def _rebuild_items(self, items: List[Item]) -> None:
        # 清空旧条目
        while self.flow.count():
            item = self.flow.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        for it in items:
            widget = ItemWidget(it)
            widget.clicked.connect(self._on_item_clicked)
            self.flow.addWidget(widget)

        self.flow.invalidate()

    def _on_item_clicked(self, item: Item) -> None:
        self.item_clicked.emit(item)

    def hide_navbar(self) -> None:
        self.hide()

    @property
    def is_visible(self) -> bool:
        return self.isVisible()

    def geometry_rect(self):
        """返回窗口全局几何 (x, y, w, h)，用于外部点击检测。"""
        if not self.isVisible():
            return None
        geo = self.frameGeometry()
        return (geo.x(), geo.y(), geo.width(), geo.height())
