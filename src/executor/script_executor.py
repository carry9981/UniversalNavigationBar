"""脚本执行器。"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
from typing import Optional

from .base import BaseExecutor

from ..config.models import Context, Item
from ..utils.variables import replace_variables


class ScriptExecutor(BaseExecutor):
    """运行 Python 插件脚本，支持同步/异步、超时、环境变量与命令行参数。"""

    def __init__(self, plugin_dir: Optional[str] = None) -> None:
        self.plugin_dir = plugin_dir or ""

    def resolve_script(self, script: str) -> str:
        """解析脚本路径（相对 plugins/ 目录或绝对路径）。"""
        if os.path.isabs(script):
            return script
        if self.plugin_dir and os.path.exists(os.path.join(self.plugin_dir, script)):
            return os.path.join(self.plugin_dir, script)
        return script

    def build_args(self, args: list, context: Context) -> list[str]:
        """对参数列表做变量替换。"""
        mapping = context.as_mapping()
        return [replace_variables(str(a), mapping, True) for a in args]

    @staticmethod
    def python_executable() -> str:
        """返回用于执行插件的 Python 解释器。

        打包（PyInstaller）后 ``sys.executable`` 是 exe 本身，不能当解释器用，
        因此回退到系统 ``python``（可用环境变量 ``UNB_PYTHON`` 覆盖）。
        """
        if getattr(sys, "frozen", False):
            return os.environ.get("UNB_PYTHON", "python")
        return sys.executable

    def run(self, item: Item, context: Context) -> None:
        config = item.config
        script = self.resolve_script(config.get("script", ""))
        args = self.build_args(config.get("args", []), context)
        timeout_sec = int(config.get("timeout_sec", 30))
        run_async = bool(config.get("run_async", False))

        command = [self.python_executable(), script, *args]
        env = dict(os.environ)
        env.update(context.to_env())

        # 以插件目录为工作目录，便于脚本使用相对路径读取资源
        cwd = self.plugin_dir if self.plugin_dir and os.path.isdir(self.plugin_dir) else None

        if run_async:
            threading.Thread(
                target=self._run_subprocess,
                args=(command, env, timeout_sec, cwd),
                daemon=True,
            ).start()
        else:
            self._run_subprocess(command, env, timeout_sec, cwd)

    def _run_subprocess(self, command: list, env: dict, timeout_sec: int, cwd: Optional[str] = None) -> None:
        try:
            subprocess.run(
                command,
                env=env,
                cwd=cwd,
                timeout=timeout_sec if timeout_sec > 0 else None,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except subprocess.TimeoutExpired:
            print(f"[script] 脚本执行超时: {command}")
        except Exception as exc:  # pragma: no cover
            print(f"[script] 脚本执行失败: {exc}")
