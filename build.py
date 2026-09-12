"""PyInstaller 打包脚本。

用法：
    python build.py

生成单文件 exe 到 dist/UniversalNavBar.exe。
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        "UniversalNavBar",
        "--add-data",
        f"plugins{os.pathsep}plugins",
        "--icon",
        "resources/tray_icon.ico",
        os.path.join("src", "main.py"),
    ]
    print("运行:", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
