"""配置模块单元测试。"""
import json
import os
import shutil
import tempfile
import unittest

from src.config.defaults import default_config
from src.config.manager import ConfigManager
from src.config.models import ConfigError, Item


class TestItemModel(unittest.TestCase):
    def test_from_dict_valid(self):
        item = Item.from_dict(
            {
                "id": "i1",
                "name": "复制",
                "icon": "📋",
                "type": "hotkey",
                "enabled": True,
                "order": 0,
                "config": {"keys": ["ctrl", "c"]},
            }
        )
        self.assertEqual(item.id, "i1")
        self.assertEqual(item.name, "复制")
        self.assertEqual(item.type, "hotkey")

    def test_from_dict_missing_name(self):
        with self.assertRaises(ConfigError):
            Item.from_dict({"type": "hotkey", "config": {"keys": ["ctrl", "c"]}})

    def test_from_dict_invalid_type(self):
        with self.assertRaises(ConfigError):
            Item.from_dict({"name": "x", "type": "bogus", "config": {}})

    def test_from_dict_missing_config(self):
        with self.assertRaises(ConfigError):
            Item.from_dict({"name": "x", "type": "hotkey"})

    def test_hotkey_missing_keys(self):
        with self.assertRaises(ConfigError):
            Item.from_dict({"name": "x", "type": "hotkey", "config": {}})

    def test_text_missing_content(self):
        with self.assertRaises(ConfigError):
            Item.from_dict({"name": "x", "type": "text", "config": {}})

    def test_script_missing_script(self):
        with self.assertRaises(ConfigError):
            Item.from_dict({"name": "x", "type": "script", "config": {}})

    def test_roundtrip(self):
        item = Item.from_dict(
            {"id": "i1", "name": "搜索", "type": "script", "config": {"script": "s.py", "args": ["{selected_text}"]}}
        )
        self.assertEqual(Item.from_dict(item.to_dict()).to_dict(), item.to_dict())


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_creates_default_config(self):
        cm = ConfigManager(self.tmp)
        self.assertIn("items", cm.data)
        self.assertEqual(len(cm.get_items()), 7)

    def test_save_and_reload(self):
        cm = ConfigManager(self.tmp)
        cm.set(False, "trigger", "text_select", "enabled")
        cm.save()
        cm2 = ConfigManager(self.tmp)
        self.assertFalse(cm2.get("trigger", "text_select", "enabled"))

    def test_merge_preserves_defaults(self):
        cm = ConfigManager(self.tmp)
        # 写一个只含部分字段的配置
        partial = {"ui": {"theme": "light"}}
        path = os.path.join(self.tmp, "config.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(partial, f)
        cm.load()
        # 合并后既有 light 主题，也保留默认的 opacity
        self.assertEqual(cm.get("ui", "theme"), "light")
        self.assertEqual(cm.get("ui", "opacity"), 0.92)

    def test_items_sorted_by_order(self):
        cm = ConfigManager(self.tmp)
        cm.data["items"] = [
            {"id": "b", "name": "B", "type": "text", "order": 2, "config": {"content": "b"}},
            {"id": "a", "name": "A", "type": "text", "order": 1, "config": {"content": "a"}},
        ]
        items = cm.get_items()
        self.assertEqual([i.id for i in items], ["a", "b"])

    def test_ignores_invalid_items(self):
        cm = ConfigManager(self.tmp)
        cm.data["items"] = [
            {"id": "good", "name": "OK", "type": "text", "config": {"content": "x"}},
            {"id": "bad", "name": "Bad", "type": "nope", "config": {}},
        ]
        items = cm.get_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, "good")

    def test_add_update_remove(self):
        cm = ConfigManager(self.tmp)
        item = Item(name="测试", type="text", config={"content": "hello"})
        cm.add_item(item)
        self.assertEqual(len(cm.get_items()), 8)
        item.config["content"] = "world"
        self.assertTrue(cm.update_item(item))
        found = [i for i in cm.get_items() if i.id == item.id][0]
        self.assertEqual(found.config["content"], "world")
        self.assertTrue(cm.remove_item(item.id))
        self.assertFalse(cm.remove_item(item.id))


class TestPortableConfigDir(unittest.TestCase):
    def test_portable_when_config_present(self):
        from src.config.manager import resolve_config_dir

        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "config.json"), "w", encoding="utf-8") as f:
                f.write("{}")
            self.assertEqual(resolve_config_dir(root), root)

    def test_fallback_to_appdata_without_config(self):
        from src.config.defaults import APP_NAME
        from src.config.manager import resolve_config_dir

        with tempfile.TemporaryDirectory() as root:
            expected = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
            self.assertEqual(resolve_config_dir(root), expected)


class TestScriptItemViaConfig(unittest.TestCase):
    def test_add_script_item_in_config(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "items": [
                            {
                                "id": "s1",
                                "name": "我的脚本",
                                "type": "script",
                                "config": {"script": "my.py", "args": ["{selected_text}"]},
                            }
                        ]
                    },
                    f,
                    ensure_ascii=False,
                )
            cm = ConfigManager(d)
            items = cm.get_items()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].type, "script")
            self.assertEqual(items[0].config["script"], "my.py")


if __name__ == "__main__":
    unittest.main()
