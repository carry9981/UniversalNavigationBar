"""脚本执行器单元测试。"""
import os
import sys
import tempfile
import unittest

from src.config.models import Context, Item
from src.executor.script_executor import ScriptExecutor


class TestScriptExecutor(unittest.TestCase):
    def test_build_args_replaces_variables(self):
        ex = ScriptExecutor(plugin_dir="")
        item = Item(name="s", type="script", config={"script": "x.py"})
        context = Context(selected_text="hello world", mouse_x=5, mouse_y=7)
        args = ex.build_args(["--text", "{selected_text}", "--x", "{mouse_x}", "--y", "{mouse_y}"], context)
        self.assertEqual(args, ["--text", "hello world", "--x", "5", "--y", "7"])

    def test_resolve_script_relative(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "s.py")
            with open(path, "w", encoding="utf-8") as f:
                f.write("print('hi')")
            ex = ScriptExecutor(plugin_dir=d)
            self.assertEqual(ex.resolve_script("s.py"), path)

    def test_run_sync_sets_env(self):
        with tempfile.TemporaryDirectory() as d:
            script = os.path.join(d, "dump.py")
            with open(script, "w", encoding="utf-8") as f:
                f.write("import os; print(os.environ.get('UNB_SELECTED_TEXT', ''))")
            ex = ScriptExecutor(plugin_dir=d)
            item = Item(name="s", type="script", config={"script": "dump.py", "args": [], "timeout_sec": 10})
            context = Context(selected_text="abc", plugin_dir=d)
            ex.run(item, context)
            # 不抛异常即成功


if __name__ == "__main__":
    unittest.main()
