"""默认配置。"""
from __future__ import annotations

APP_NAME = "UniversalNavBar"
APP_DISPLAY_NAME = "Universal Navigation Bar"
APP_VERSION = "1.0.0"


def default_config() -> dict:
    """返回一份完整的默认配置字典。"""
    return {
        "version": APP_VERSION,
        "trigger": {
            "text_select": {
                "enabled": True,
                "min_distance_px": 15,
                "max_duration_sec": 2.0,
            },
            "left_click_hold": {
                "enabled": True,
                "hold_duration_sec": 0.5,
                "move_tolerance_px": 6,
            },
        },
        "text_getter": {
            "method": "uiautomation",
            "fallback_to_clipboard": True,
            "clipboard_restore": True,
            "cache_duration_ms": 500,
        },
        "ui": {
            "theme": "dark",
            "opacity": 0.92,
            "border_radius_px": 10,
            "font_family": "Microsoft YaHei, sans-serif",
            "font_size_px": 13,
            "item_padding_px": 8,
            "max_width_px": 400,
            "position_offset_px": 15,
            "shadow": True,
            "blur_background": True,
        },
        "items": [
            {
                "id": "builtin_select_all",
                "name": "全选",
                "icon": "✅",
                "type": "hotkey",
                "enabled": True,
                "order": 0,
                "config": {
                    "keys": ["ctrl", "a"],
                    "delay_ms": 50,
                },
            },
            {
                "id": "builtin_copy",
                "name": "复制",
                "icon": "📋",
                "type": "hotkey",
                "enabled": True,
                "order": 1,
                "config": {
                    "keys": ["ctrl", "c"],
                    "delay_ms": 50,
                },
            },
            {
                "id": "builtin_paste",
                "name": "粘贴",
                "icon": "📌",
                "type": "hotkey",
                "enabled": True,
                "order": 2,
                "config": {
                    "keys": ["ctrl", "v"],
                    "delay_ms": 50,
                },
            },
            {
                "id": "builtin_clipboard_history",
                "name": "剪贴板历史",
                "icon": "🕘",
                "type": "hotkey",
                "enabled": True,
                "order": 3,
                "config": {
                    "keys": ["win", "v"],
                    "delay_ms": 50,
                },
            },
            {
                "id": "builtin_voice_input",
                "name": "语音输入",
                "icon": "🎤",
                "type": "hotkey",
                "enabled": True,
                "order": 4,
                "config": {
                    "keys": ["ctrl", "f2"],
                    "delay_ms": 50,
                },
            },
            {
                "id": "builtin_search",
                "name": "逗号",
                "icon": "，",
                "type": "text",
                "enabled": True,
                "order": 5,
                "config": {
                    "content": ",",
                    "mode": "type",
                    "delay_ms": 10,
                    "variables": False,
                },
            },
            {
                "id": "builtin_greeting",
                "name": "句号",
                "icon": "。",
                "type": "text",
                "enabled": True,
                "order": 6,
                "config": {
                    "content": "。",
                    "mode": "type",
                    "delay_ms": 10,
                    "variables": False,
                },
            },
        ],
        "general": {
            "auto_start": True,
            "check_updates": True,
        },
    }
