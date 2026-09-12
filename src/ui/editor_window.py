"""条目管理窗口。"""
from __future__ import annotations

import json
import uuid
from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from ..config.models import ConfigError, Item
from .item_dialog import ItemDialog


class EditorWindow(QDialog):
    """可视化管理条目。"""

    def __init__(self, config_manager, parent=None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("📝 条目管理")
        self.resize(520, 480)
        self._items: List[Item] = []

        self._build_ui()
        self.reload_items()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(lambda _: self._edit_item())
        layout.addWidget(self.list_widget)

        # 行操作按钮
        row_buttons = QHBoxLayout()
        btn_up = QPushButton("↑ 上移")
        btn_up.clicked.connect(self._move_up)
        btn_down = QPushButton("↓ 下移")
        btn_down.clicked.connect(self._move_down)
        btn_edit = QPushButton("✏ 编辑")
        btn_edit.clicked.connect(self._edit_item)
        btn_del = QPushButton("🗑 删除")
        btn_del.clicked.connect(self._delete_item)
        for b in (btn_up, btn_down, btn_edit, btn_del):
            row_buttons.addWidget(b)
        layout.addLayout(row_buttons)

        # 底部按钮
        bottom = QHBoxLayout()
        btn_add = QPushButton("➕ 添加")
        btn_add.clicked.connect(self._add_item)
        btn_import = QPushButton("📥 导入")
        btn_import.clicked.connect(self._import_items)
        btn_export = QPushButton("📤 导出")
        btn_export.clicked.connect(self._export_items)
        btn_save = QPushButton("💾 保存更改")
        btn_save.clicked.connect(self._save)
        for b in (btn_add, btn_import, btn_export, btn_save):
            bottom.addWidget(b)
        layout.addLayout(bottom)

    # ------------------------------------------------------------- 数据
    def reload_items(self) -> None:
        self._items = [Item.from_dict(it.to_dict()) for it in self.config_manager.all_items()]
        self._refresh_list()

    def _refresh_list(self) -> None:
        self.list_widget.clear()
        for item in self._items:
            text = f"{item.icon + '  ' if item.icon else ''}{item.name}  ({item.type})"
            list_item = QListWidgetItem(text)
            list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            list_item.setCheckState(Qt.CheckState.Checked if item.enabled else Qt.CheckState.Unchecked)
            self.list_widget.addItem(list_item)

    def _sync_checks(self) -> None:
        for i, item in enumerate(self._items):
            list_item = self.list_widget.item(i)
            if list_item is not None:
                item.enabled = list_item.checkState() == Qt.CheckState.Checked

    def _current_index(self) -> int:
        return self.list_widget.currentRow()

    # ------------------------------------------------------------- 操作
    def _add_item(self) -> None:
        dialog = ItemDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item = dialog.get_item()
            self._items.append(item)
            self._refresh_list()

    def _edit_item(self) -> None:
        idx = self._current_index()
        if idx < 0:
            return
        dialog = ItemDialog(self._items[idx], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._items[idx] = dialog.get_item()
            self._refresh_list()

    def _delete_item(self) -> None:
        idx = self._current_index()
        if idx < 0:
            return
        del self._items[idx]
        self._refresh_list()

    def _move_up(self) -> None:
        idx = self._current_index()
        if 0 < idx < len(self._items):
            self._items[idx], self._items[idx - 1] = self._items[idx - 1], self._items[idx]
            self._refresh_list()
            self.list_widget.setCurrentRow(idx - 1)

    def _move_down(self) -> None:
        idx = self._current_index()
        if 0 <= idx < len(self._items) - 1:
            self._items[idx], self._items[idx + 1] = self._items[idx + 1], self._items[idx]
            self._refresh_list()
            self.list_widget.setCurrentRow(idx + 1)

    def _export_items(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "导出条目", "items.json", "JSON (*.json)")
        if not path:
            return
        self._sync_checks()
        data = [it.to_dict() for it in self._items]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "导出", f"已导出 {len(data)} 个条目到 {path}")

    def _import_items(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "导入条目", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("导入文件必须是条目数组")
            for raw in data:
                try:
                    self._items.append(Item.from_dict(raw))
                except ConfigError as exc:
                    QMessageBox.warning(self, "导入", f"忽略无效条目: {exc}")
            self._refresh_list()
        except Exception as exc:
            QMessageBox.warning(self, "导入", f"导入失败: {exc}")

    def _save(self) -> None:
        self._sync_checks()
        for i, item in enumerate(self._items):
            item.order = i
        self.config_manager.set_items(self._items)
        self.config_manager.save()
        QMessageBox.information(self, "保存", "条目已保存，配置已更新")
        self.accept()
