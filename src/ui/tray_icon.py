"""系统托盘。"""
from __future__ import annotations

import os

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

from ..config.defaults import APP_DISPLAY_NAME


def create_app_icon(size: int = 64) -> QIcon:
    """程序化生成应用图标（无需外部 .ico 资源）。"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#1E1E2E"))
    painter.setPen(QColor("#89B4FA"))
    painter.drawEllipse(2, 2, size - 4, size - 4)
    painter.setFont(QFont("Segoe UI Emoji", int(size * 0.5)))
    painter.setPen(QColor("#CDD6F4"))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🧭")
    painter.end()
    return QIcon(pixmap)


class TrayIcon(QObject):
    """系统托盘图标与菜单。"""

    manage_items = pyqtSignal()
    open_settings = pyqtSignal()
    reload_config = pyqtSignal()
    quit_requested = pyqtSignal()
    auto_start_toggled = pyqtSignal(bool)

    def __init__(self, config_manager, plugin_dir: str = "", parent=None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.plugin_dir = plugin_dir or "."
        self.tray = QSystemTrayIcon(create_app_icon(), parent)
        self.tray.setToolTip(APP_DISPLAY_NAME)
        self._build_menu()
        self.tray.show()

    def _build_menu(self) -> None:
        # 注意：QSystemTrayIcon 不持有菜单所有权，必须保留引用，否则菜单会被回收
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                color: #000000;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
                color: #000000;
            }
            QMenu::item:disabled {
                color: #888888;
            }
            QMenu::separator {
                height: 1px;
                background: #CCCCCC;
                margin: 4px 8px;
            }
        """)
        menu = self.menu

        self.act_title = QAction(f"🧭 {APP_DISPLAY_NAME}")
        self.act_title.setEnabled(False)
        menu.addAction(self.act_title)
        menu.addSeparator()

        self.act_manage = QAction("📝 管理条目…")
        self.act_manage.triggered.connect(self.manage_items.emit)
        menu.addAction(self.act_manage)

        self.act_settings = QAction("⚙ 打开设置…")
        self.act_settings.triggered.connect(self.open_settings.emit)
        menu.addAction(self.act_settings)

        self.act_config_dir = QAction("📂 打开配置文件夹")
        self.act_config_dir.triggered.connect(lambda: self._open_path(self.config_manager.config_dir))
        menu.addAction(self.act_config_dir)

        plugin_dir = self.plugin_dir
        self.act_plugin_dir = QAction("📂 打开插件文件夹")
        self.act_plugin_dir.triggered.connect(lambda: self._open_path(plugin_dir or "."))
        menu.addAction(self.act_plugin_dir)

        menu.addSeparator()

        self.act_reload = QAction("🔄 重新加载配置")
        self.act_reload.triggered.connect(self.reload_config.emit)
        menu.addAction(self.act_reload)

        self.act_auto_start = QAction("🚀 开机自启动")
        self.act_auto_start.setCheckable(True)
        self.act_auto_start.setChecked(bool(self.config_manager.get("general", "auto_start", default=False)))
        self.act_auto_start.toggled.connect(self.auto_start_toggled.emit)
        menu.addAction(self.act_auto_start)

        menu.addSeparator()

        self.act_quit = QAction("❌ 退出")
        self.act_quit.triggered.connect(self.quit_requested.emit)
        menu.addAction(self.act_quit)

        self.tray.setContextMenu(self.menu)

    def set_auto_start_checked(self, checked: bool) -> None:
        self.act_auto_start.blockSignals(True)
        self.act_auto_start.setChecked(checked)
        self.act_auto_start.blockSignals(False)

    @staticmethod
    def _open_path(path: str) -> None:
        try:
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception:
            pass

    def show_message(self, title: str, message: str) -> None:
        self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)
