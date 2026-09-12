"""应用主类：整合配置、触发、文本获取、界面与动作执行。"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from .config import APP_NAME, ConfigManager, Context
from .executor import ActionExecutor
from .text_getter import TextGetter
from .trigger import TriggerEvent, TriggerManager
from .ui import EditorWindow, NavBar, TrayIcon
from .ui.styles import build_stylesheet
from .utils import autostart
from .utils.clipboard import get_clipboard_text


def _active_window_title() -> str:
    """获取活动窗口标题。"""
    try:
        import uiautomation as auto

        control = auto.GetForegroundControl()
        if control is not None:
            name = control.Name
            if name:
                return str(name)
    except Exception:
        pass
    return ""


class Bridge(QObject):
    """跨线程信号桥，将监听线程的事件转发到 Qt 主线程。"""

    triggered = pyqtSignal(object)  # TriggerEvent 或 None
    escape = pyqtSignal()
    outside_click = pyqtSignal(object)  # (x, y)


class Application(QObject):
    """UNB 应用主类。"""

    def __init__(self, app, config_dir: Optional[str] = None) -> None:
        super().__init__()
        self.qt_app = app
        self.config_manager = ConfigManager(config_dir)
        self.plugin_dir = os.environ.get("UNB_PLUGIN_DIR") or self._resolve_plugin_dir()

        self.stylesheet = build_stylesheet(self.config_manager.get("ui", default={}))
        self.qt_app.setStyleSheet(self.stylesheet)

        self.text_getter = TextGetter(self.config_manager.get("text_getter", default={}))
        self.executor = ActionExecutor(plugin_dir=self.plugin_dir)

        self.bridge = Bridge()
        self.navbar = NavBar(
            ui_config=self.config_manager.get("ui", default={}),
            stylesheet=self.stylesheet,
        )
        self.tray = TrayIcon(self.config_manager, plugin_dir=self.plugin_dir, parent=self)

        self.trigger_manager = TriggerManager(
            config=self.config_manager.get("trigger", default={}),
            on_trigger=self.bridge.triggered.emit,
            on_escape=self.bridge.escape.emit,
            on_outside_click=self.bridge.outside_click.emit,
        )

        self._connect_signals()
        self._last_pos = (0, 0)

    # ------------------------------------------------------------- 初始化
    def _resolve_plugin_dir(self) -> str:
        # 软件根目录（src 的上一级）
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(root, "plugins")

    def _connect_signals(self) -> None:
        self.bridge.triggered.connect(self._on_triggered)
        self.bridge.escape.connect(self._on_escape)
        self.bridge.outside_click.connect(self._on_outside_click)
        self.navbar.item_clicked.connect(self._on_item_clicked)

        self.tray.manage_items.connect(self._open_editor)
        self.tray.open_settings.connect(self._open_settings)
        self.tray.reload_config.connect(self._reload_config)
        self.tray.quit_requested.connect(self._quit)
        self.tray.auto_start_toggled.connect(self._toggle_auto_start)

    def start(self) -> None:
        self.trigger_manager.start()
        self._apply_auto_start()

    # ------------------------------------------------------------- 触发处理
    def _on_triggered(self, event: Optional[TriggerEvent]) -> None:
        if event is None:
            # 关闭信号（保留兼容），关闭导航条
            if self.navbar.is_visible:
                self.navbar.hide_navbar()
                self.trigger_manager.set_navbar_rect(None)
            return

        # 已显示时再次触发 → toggle 关闭
        if self.navbar.is_visible:
            self.navbar.hide_navbar()
            self.trigger_manager.set_navbar_rect(None)
            return

        self._last_pos = (int(event.x), int(event.y))
        self.text_getter.invalidate_cache()
        selected_text = self.text_getter.get_selected_text()

        context = Context(
            selected_text=selected_text,
            clipboard=get_clipboard_text(),
            mouse_x=int(event.x),
            mouse_y=int(event.y),
            active_window=_active_window_title(),
            trigger_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            trigger_source=event.source,
            config_dir=self.config_manager.config_dir,
            plugin_dir=self.plugin_dir,
        )

        items = self.config_manager.get_items(enabled_only=True)
        if not items:
            return
        self.navbar.show_items(items, (event.x, event.y))
        self._sync_navbar_rect()

    def _on_escape(self) -> None:
        if self.navbar.is_visible:
            self.navbar.hide_navbar()
            self.trigger_manager.set_navbar_rect(None)

    def _on_outside_click(self, _pos) -> None:
        if self.navbar.is_visible:
            self.navbar.hide_navbar()
            self.trigger_manager.set_navbar_rect(None)

    def _on_item_clicked(self, item) -> None:
        context = Context(
            selected_text=self.text_getter.get_selected_text(),
            clipboard=get_clipboard_text(),
            mouse_x=self._last_pos[0],
            mouse_y=self._last_pos[1],
            active_window=_active_window_title(),
            trigger_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            item_id=item.id,
            item_name=item.name,
            config_dir=self.config_manager.config_dir,
            plugin_dir=self.plugin_dir,
        )
        self.navbar.hide_navbar()
        self.trigger_manager.set_navbar_rect(None)
        try:
            self.executor.execute(item, context)
        except Exception as exc:
            self.tray.show_message("执行失败", str(exc))

    def _sync_navbar_rect(self) -> None:
        rect = self.navbar.geometry_rect()
        self.trigger_manager.set_navbar_rect(rect)

    # ------------------------------------------------------------- 托盘动作
    def _open_editor(self) -> None:
        editor = EditorWindow(self.config_manager)
        editor.exec()

    def _open_settings(self) -> None:
        try:
            os.startfile(self.config_manager.config_path)  # type: ignore[attr-defined]
        except Exception:
            self.tray.show_message("提示", "无法打开配置文件")

    def _reload_config(self) -> None:
        self.config_manager.reload()
        self.stylesheet = build_stylesheet(self.config_manager.get("ui", default={}))
        self.qt_app.setStyleSheet(self.stylesheet)
        self.navbar.setStyleSheet(self.stylesheet)
        self.text_getter = TextGetter(self.config_manager.get("text_getter", default={}))
        self.tray.show_message("提示", "配置已重新加载")

    def _toggle_auto_start(self, enabled: bool) -> None:
        self.config_manager.set(enabled, "general", "auto_start")
        self.config_manager.save()
        autostart.set_enabled(enabled)
        self.tray.set_auto_start_checked(enabled)

    def _apply_auto_start(self) -> None:
        """启动时将注册表状态与配置同步。"""
        enabled = bool(self.config_manager.get("general", "auto_start", default=False))
        if autostart.set_enabled(enabled):
            self.tray.set_auto_start_checked(enabled)

    def _quit(self) -> None:
        self.trigger_manager.stop()
        self.qt_app.quit()
