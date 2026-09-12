"""变量替换与执行器单元测试。"""
import unittest
from unittest import mock

from src.config.models import Context, Item
from src.utils.variables import replace_variables


class TestVariables(unittest.TestCase):
    def test_basic_replace(self):
        result = replace_variables(
            "你好 {selected_text}",
            {"selected_text": "世界"},
        )
        self.assertEqual(result, "你好 世界")

    def test_date_and_time(self):
        result = replace_variables("{date}", {})
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2}")

    def test_newline(self):
        result = replace_variables("a{newline}b", {})
        self.assertEqual(result, "a\nb")

    def test_disabled(self):
        result = replace_variables("{selected_text}", {"selected_text": "x"}, enabled=False)
        self.assertEqual(result, "{selected_text}")

    def test_unknown_variable(self):
        result = replace_variables("{unknown}", {})
        self.assertEqual(result, "")

    def test_none_value(self):
        result = replace_variables("{selected_text}", {"selected_text": None})
        self.assertEqual(result, "")


class TestHotkeyResolver(unittest.TestCase):
    def test_resolve_key(self):
        from src.executor.hotkey_executor import resolve_key

        self.assertIsNotNone(resolve_key("ctrl"))
        self.assertIsNotNone(resolve_key("shift"))
        self.assertIsNotNone(resolve_key("win"))
        self.assertIsNotNone(resolve_key("a"))
        self.assertIsNotNone(resolve_key("f5"))
        self.assertIsNotNone(resolve_key("f2"))
        self.assertIsNotNone(resolve_key("enter"))
        self.assertIsNone(resolve_key("not_a_key"))


class TestTextExecutor(unittest.TestCase):
    def test_variable_replacement_in_content(self):
        from src.executor.text_executor import TextExecutor

        item = Item(
            name="x",
            type="text",
            config={"content": "选中: {selected_text}", "mode": "type", "delay_ms": 0, "variables": True},
        )
        context = Context(selected_text="hello")
        executor = TextExecutor()
        with mock.patch.object(executor, "_type") as m_type, mock.patch.object(executor, "_paste") as m_paste:
            executor.run(item, context)
            m_type.assert_called_once_with("选中: hello", 0)
            m_paste.assert_not_called()

    def test_paste_mode(self):
        from src.executor.text_executor import TextExecutor

        item = Item(
            name="x",
            type="text",
            config={"content": "hello", "mode": "paste", "delay_ms": 0, "variables": False},
        )
        executor = TextExecutor()
        with mock.patch.object(executor, "_paste") as m_paste, mock.patch.object(executor, "_type") as m_type:
            executor.run(item, Context())
            m_paste.assert_called_once_with("hello")
            m_type.assert_not_called()


if __name__ == "__main__":
    unittest.main()
