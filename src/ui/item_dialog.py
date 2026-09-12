"""添加/编辑条目对话框。"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..config.models import Item


class ItemDialog(QDialog):
    """新增或编辑一个条目。"""

    def __init__(self, item: Optional[Item] = None, parent=None) -> None:
        super().__init__(parent)
        self._editing = item
        self.setWindowTitle("编辑条目" if item else "添加条目")
        self.setMinimumWidth(420)
        self._build_ui()
        if item:
            self._populate(item)
        self._on_type_changed(self.type_combo.currentIndex())

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow("名称", self.name_edit)

        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("Emoji 图标，如 📋")
        form.addRow("图标", self.icon_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItem("快捷键", "hotkey")
        self.type_combo.addItem("预设文本", "text")
        self.type_combo.addItem("脚本", "script")
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("类型", self.type_combo)

        self.enabled_check = QCheckBox("启用")
        self.enabled_check.setChecked(True)
        form.addRow("", self.enabled_check)

        self.order_spin = QSpinBox()
        self.order_spin.setRange(-9999, 9999)
        form.addRow("排序", self.order_spin)

        layout.addLayout(form)

        # 类型专属配置
        self.config_stack = QStackedWidget()
        self.config_stack.addWidget(self._build_hotkey_widget())
        self.config_stack.addWidget(self._build_text_widget())
        self.config_stack.addWidget(self._build_script_widget())
        layout.addWidget(self.config_stack)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------- 配置面板
    def _build_hotkey_widget(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.hotkey_keys = QLineEdit()
        self.hotkey_keys.setPlaceholderText("逗号分隔，如 ctrl, c 或 ctrl, shift, s")
        form.addRow("按键", self.hotkey_keys)
        self.hotkey_delay = QSpinBox()
        self.hotkey_delay.setRange(0, 5000)
        self.hotkey_delay.setValue(50)
        self.hotkey_delay.setSuffix(" ms")
        form.addRow("间隔", self.hotkey_delay)
        return w

    def _build_text_widget(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.text_content = QPlainTextEdit()
        self.text_content.setPlaceholderText("要输入的文本，支持 {selected_text} 等变量")
        form.addRow("内容", self.text_content)
        self.text_mode = QComboBox()
        self.text_mode.addItem("逐字符输入", "type")
        self.text_mode.addItem("剪贴板粘贴", "paste")
        form.addRow("方式", self.text_mode)
        self.text_delay = QSpinBox()
        self.text_delay.setRange(0, 5000)
        self.text_delay.setValue(10)
        self.text_delay.setSuffix(" ms")
        form.addRow("字符间隔", self.text_delay)
        self.text_variables = QCheckBox("启用变量替换")
        self.text_variables.setChecked(True)
        form.addRow("", self.text_variables)
        return w

    def _build_script_widget(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.script_path = QLineEdit()
        self.script_path.setPlaceholderText("plugins/ 目录下的脚本文件名，如 search_web.py")
        form.addRow("脚本", self.script_path)
        self.script_args = QLineEdit()
        self.script_args.setPlaceholderText("空格分隔的参数，如 {selected_text}")
        form.addRow("参数", self.script_args)
        self.script_timeout = QSpinBox()
        self.script_timeout.setRange(0, 3600)
        self.script_timeout.setValue(30)
        self.script_timeout.setSuffix(" s")
        form.addRow("超时", self.script_timeout)
        self.script_async = QCheckBox("异步执行（不阻塞界面）")
        self.script_async.setChecked(False)
        form.addRow("", self.script_async)
        return w

    # ------------------------------------------------------------- 逻辑
    def _on_type_changed(self, index: int) -> None:
        self.config_stack.setCurrentIndex(index)

    def _populate(self, item: Item) -> None:
        self.name_edit.setText(item.name)
        self.icon_edit.setText(item.icon)
        idx = self.type_combo.findData(item.type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.enabled_check.setChecked(item.enabled)
        self.order_spin.setValue(item.order)
        cfg = item.config or {}
        if item.type == "hotkey":
            self.hotkey_keys.setText(", ".join(cfg.get("keys", [])))
            self.hotkey_delay.setValue(int(cfg.get("delay_ms", 50)))
        elif item.type == "text":
            self.text_content.setPlainText(cfg.get("content", ""))
            mode_idx = self.text_mode.findData(cfg.get("mode", "type"))
            if mode_idx >= 0:
                self.text_mode.setCurrentIndex(mode_idx)
            self.text_delay.setValue(int(cfg.get("delay_ms", 10)))
            self.text_variables.setChecked(bool(cfg.get("variables", True)))
        elif item.type == "script":
            self.script_path.setText(cfg.get("script", ""))
            self.script_args.setText(" ".join(cfg.get("args", [])))
            self.script_timeout.setValue(int(cfg.get("timeout_sec", 30)))
            self.script_async.setChecked(bool(cfg.get("run_async", False)))

    def _validate_and_accept(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "名称不能为空")
            return
        try:
            self.get_item()
        except ValueError as exc:
            QMessageBox.warning(self, "提示", str(exc))
            return
        self.accept()

    def get_item(self) -> Item:
        item_type = self.type_combo.currentData()
        config: dict = {}
        if item_type == "hotkey":
            keys = [k.strip().lower() for k in self.hotkey_keys.text().split(",") if k.strip()]
            if not keys:
                raise ValueError("快捷键至少需要一个按键")
            config = {"keys": keys, "delay_ms": self.hotkey_delay.value()}
        elif item_type == "text":
            config = {
                "content": self.text_content.toPlainText(),
                "mode": self.text_mode.currentData(),
                "delay_ms": self.text_delay.value(),
                "variables": self.text_variables.isChecked(),
            }
        elif item_type == "script":
            script = self.script_path.text().strip()
            if not script:
                raise ValueError("脚本文件名不能为空")
            args = [a for a in self.script_args.text().split(" ") if a.strip()]
            config = {
                "script": script,
                "args": args,
                "timeout_sec": self.script_timeout.value(),
                "run_async": self.script_async.isChecked(),
            }

        item = Item(
            name=self.name_edit.text().strip(),
            icon=self.icon_edit.text().strip(),
            type=item_type,
            enabled=self.enabled_check.isChecked(),
            order=self.order_spin.value(),
            config=config,
        )
        if self._editing:
            item.id = self._editing.id
        item.validate()
        return item
