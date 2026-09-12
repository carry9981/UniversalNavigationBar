"""触发模块单元测试。"""
import time
import unittest

from src.trigger.left_click_hold import LeftClickHoldTrigger
from src.trigger.text_select import TextSelectTrigger


class TestTextSelectTrigger(unittest.TestCase):
    def setUp(self):
        self.events = []

    def _handler(self, event):
        self.events.append(event)

    def test_drag_triggers(self):
        t = TextSelectTrigger({"enabled": True, "min_distance_px": 15, "max_duration_sec": 2.0}, self._handler)
        t.on_click(0, 0, "left", True)
        t.on_move(50, 0)
        t.on_click(50, 0, "left", False)
        self.assertEqual(len(self.events), 1)
        self.assertEqual((self.events[0].x, self.events[0].y), (50, 0))
        self.assertEqual(self.events[0].source, "text_select")

    def test_click_does_not_trigger(self):
        t = TextSelectTrigger({"enabled": True, "min_distance_px": 15, "max_duration_sec": 2.0}, self._handler)
        t.on_click(0, 0, "left", True)
        t.on_click(2, 2, "left", False)
        self.assertEqual(len(self.events), 0)

    def test_slow_drag_does_not_trigger(self):
        t = TextSelectTrigger({"enabled": True, "min_distance_px": 15, "max_duration_sec": 0.01}, self._handler)
        t.on_click(0, 0, "left", True)
        time.sleep(0.05)
        t.on_click(50, 0, "left", False)
        self.assertEqual(len(self.events), 0)

    def test_disabled(self):
        t = TextSelectTrigger({"enabled": False, "min_distance_px": 15, "max_duration_sec": 2.0}, self._handler)
        t.on_click(0, 0, "left", True)
        t.on_click(50, 0, "left", False)
        self.assertEqual(len(self.events), 0)


class TestLeftClickHoldTrigger(unittest.TestCase):
    def setUp(self):
        self.events = []

    def _handler(self, event):
        self.events.append(event)

    def test_hold_triggers(self):
        t = LeftClickHoldTrigger({"enabled": True, "hold_duration_sec": 0.05}, self._handler)
        t.on_click(10, 10, "left", True)
        time.sleep(0.15)
        self.assertEqual(len(self.events), 1)
        self.assertEqual((self.events[0].x, self.events[0].y), (10, 10))
        self.assertEqual(self.events[0].source, "left_click_hold")
        t.on_click(10, 10, "left", False)

    def test_quick_click_no_trigger(self):
        t = LeftClickHoldTrigger({"enabled": True, "hold_duration_sec": 0.2}, self._handler)
        t.on_click(10, 10, "left", True)
        time.sleep(0.02)
        t.on_click(10, 10, "left", False)
        time.sleep(0.25)
        self.assertEqual(len(self.events), 0)

    def test_hold_then_drag_no_trigger(self):
        t = LeftClickHoldTrigger(
            {"enabled": True, "hold_duration_sec": 0.05, "move_tolerance_px": 6}, self._handler
        )
        t.on_click(0, 0, "left", True)
        t.on_move(50, 0)  # 拖动
        time.sleep(0.15)
        self.assertEqual(len(self.events), 0)

    def test_small_jitter_still_triggers(self):
        t = LeftClickHoldTrigger(
            {"enabled": True, "hold_duration_sec": 0.05, "move_tolerance_px": 6}, self._handler
        )
        t.on_click(0, 0, "left", True)
        t.on_move(2, 1)  # 轻微抖动，视为未拖动
        time.sleep(0.15)
        self.assertEqual(len(self.events), 1)

    def test_disabled(self):
        t = LeftClickHoldTrigger({"enabled": False, "hold_duration_sec": 0.05}, self._handler)
        t.on_click(10, 10, "left", True)
        time.sleep(0.15)
        self.assertEqual(len(self.events), 0)

    def test_right_button_ignored(self):
        t = LeftClickHoldTrigger({"enabled": True, "hold_duration_sec": 0.05}, self._handler)
        t.on_click(10, 10, "right", True)
        time.sleep(0.15)
        self.assertEqual(len(self.events), 0)


class TestTriggerManager(unittest.TestCase):
    def test_hold_fired_then_release_no_text_select(self):
        from src.trigger import TriggerManager

        calls = []
        mgr = TriggerManager(
            config={"left_click_hold": {"enabled": True, "hold_duration_sec": 0.05}},
            on_trigger=lambda e: calls.append(e),
        )
        # 按下并长按触发
        mgr._on_click(0, 0, _FakeButton("left"), True)
        time.sleep(0.15)
        hold_events = [e for e in calls if e is not None and e.source == "left_click_hold"]
        self.assertEqual(len(hold_events), 1)
        # 触发后再拖动并松开，不应再次由框选触发
        mgr._on_move(50, 0)
        mgr._on_click(50, 0, _FakeButton("left"), False)
        text_events = [e for e in calls if e is not None and e.source == "text_select"]
        self.assertEqual(len(text_events), 0)

    def test_outside_click_closes_when_navbar_visible(self):
        from src.trigger import TriggerManager

        outside = []
        mgr = TriggerManager(config={}, on_trigger=lambda e: None, on_outside_click=lambda p: outside.append(p))
        mgr.set_navbar_rect((0, 0, 100, 100))
        mgr._on_click(200, 200, _FakeButton("left"), True)
        self.assertEqual(len(outside), 1)
        self.assertEqual(outside[0], (200, 200))

    def test_inside_click_not_outside(self):
        from src.trigger import TriggerManager

        outside = []
        mgr = TriggerManager(config={}, on_trigger=lambda e: None, on_outside_click=lambda p: outside.append(p))
        mgr.set_navbar_rect((0, 0, 100, 100))
        mgr._on_click(50, 50, _FakeButton("left"), True)
        self.assertEqual(len(outside), 0)


class _FakeButton:
    def __init__(self, name: str) -> None:
        self.name = name


if __name__ == "__main__":
    unittest.main()
