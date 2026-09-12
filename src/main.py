"""程序入口。"""
from __future__ import annotations

import os
import sys

from PyQt6.QtWidgets import QApplication

if __package__ in (None, ""):
    # 以脚本方式运行（python src/main.py）：将项目根目录加入 sys.path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.app import Application
else:  # 以模块方式运行（python -m src.main）
    from .app import Application


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("UniversalNavBar")
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出，常驻托盘

    application = Application(app)
    application.start()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
