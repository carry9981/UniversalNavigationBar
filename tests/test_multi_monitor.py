"""多显示器定位单元测试（offscreen 平台）。"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

_app = QApplication.instance() or QApplication([])


class TestMultiMonitor(unittest.TestCase):
    def test_clamp_to_screen(self):
        from src.ui.multi_monitor import clamp_to_screen, available_geometry_at

        geometry = available_geometry_at((100, 100))
        if geometry.isNull():
            self.skipTest("无可用屏幕")
        # 光标靠近屏幕右下角，应向左上调整
        right = geometry.right() - 5
        bottom = geometry.bottom() - 5
        x, y = clamp_to_screen(right, bottom, 300, 200, 15)
        self.assertLessEqual(x + 300, geometry.right() + 1)
        self.assertLessEqual(y + 200, geometry.bottom() + 1)


if __name__ == "__main__":
    unittest.main()
