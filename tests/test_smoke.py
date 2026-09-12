"""应用与界面冒烟测试（offscreen）。"""
import os
import shutil
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from src.config.defaults import default_config
from src.config.manager import ConfigManager
from src.config.models import Item
from src.ui.navbar import NavBar
from src.ui.styles import build_stylesheet

_app = QApplication.instance() or QApplication([])


class TestNavBar(unittest.TestCase):
    def test_show_items_and_geometry(self):
        navbar = NavBar(ui_config=default_config()["ui"], stylesheet=build_stylesheet())
        items = [Item.from_dict(x) for x in default_config()["items"]]
        navbar.show_items(items, (100, 100))
        _app.processEvents()
        self.assertTrue(navbar.is_visible)
        rect = navbar.geometry_rect()
        self.assertIsNotNone(rect)
        self.assertEqual(len(rect), 4)
        self.assertGreater(rect[2], 0)
        navbar.hide_navbar()
        self.assertFalse(navbar.is_visible)

    def test_item_clicked_signal(self):
        navbar = NavBar(ui_config=default_config()["ui"], stylesheet=build_stylesheet())
        item = Item.from_dict(default_config()["items"][0])
        received = []

        navbar.item_clicked.connect(lambda it: received.append(it))
        navbar.show_items([item], (100, 100))
        _app.processEvents()
        # 直接触发内部回调
        navbar._on_item_clicked(item)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].id, item.id)
        navbar.hide_navbar()


class TestAppConstruction(unittest.TestCase):
    def test_build(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        # 临时配置目录 + 空插件目录
        from src.app import Application

        app = Application(_app, config_dir=tmp)
        self.assertIsNotNone(app.navbar)
        self.assertIsNotNone(app.tray)
        self.assertIsNotNone(app.config_manager)
        # 不启动全局钩子，仅验证可构造

    def test_plugin_dir_resolved(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        from src.app import Application

        app = Application(_app, config_dir=tmp)
        root = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.assertEqual(app.plugin_dir, os.path.join(root, "plugins"))


class TestTrayIcon(unittest.TestCase):
    def test_menu_retained_with_quit(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        from src.config.manager import ConfigManager
        from src.ui.tray_icon import TrayIcon

        tray = TrayIcon(ConfigManager(tmp))
        # 菜单必须被持有，否则会被回收导致托盘右键无菜单
        self.assertIsNotNone(tray.menu)
        self.assertIs(tray.tray.contextMenu(), tray.menu)
        texts = [a.text() for a in tray.menu.actions()]
        self.assertTrue(any("退出" in t for t in texts))

    def test_quit_signal(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        from src.config.manager import ConfigManager
        from src.ui.tray_icon import TrayIcon

        tray = TrayIcon(ConfigManager(tmp))
        fired = []
        tray.quit_requested.connect(lambda: fired.append(True))
        tray.act_quit.trigger()
        self.assertEqual(fired, [True])


class TestManyItems(unittest.TestCase):
    def test_navbar_many_items(self):
        navbar = NavBar(ui_config=default_config()["ui"], stylesheet=build_stylesheet())
        items = []
        for i in range(30):
            items.append(Item(name=f"条目{i}", type="text", config={"content": "x"}, icon="📋", order=i))
        navbar.show_items(items, (100, 100))
        _app.processEvents()
        self.assertTrue(navbar.is_visible)
        rect = navbar.geometry_rect()
        self.assertIsNotNone(rect)
        navbar.hide_navbar()


class TestEditorWindows(unittest.TestCase):
    def test_item_dialog_roundtrip(self):
        from src.ui.item_dialog import ItemDialog

        item = Item.from_dict(
            {"id": "i1", "name": "搜索", "icon": "🔍", "type": "script",
             "enabled": True, "order": 1, "config": {"script": "s.py", "args": ["--q", "{selected_text}"], "timeout_sec": 5, "run_async": True}}
        )
        dialog = ItemDialog(item)
        result = dialog.get_item()
        self.assertEqual(result.id, "i1")
        self.assertEqual(result.name, "搜索")
        self.assertEqual(result.config["script"], "s.py")

    def test_item_dialog_new_validation(self):
        from src.ui.item_dialog import ItemDialog

        dialog = ItemDialog()
        dialog.name_edit.setText("空快捷键")
        dialog.hotkey_keys.setText("")
        with self.assertRaises(ValueError):
            dialog.get_item()

    def test_editor_window_build(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        from src.config.manager import ConfigManager
        from src.ui.editor_window import EditorWindow

        cm = ConfigManager(tmp)
        editor = EditorWindow(cm)
        self.assertEqual(editor.list_widget.count(), 7)
        # 上移最后一项
        editor.list_widget.setCurrentRow(6)
        editor._move_up()
        self.assertEqual(editor.list_widget.count(), 7)


if __name__ == "__main__":
    unittest.main()
