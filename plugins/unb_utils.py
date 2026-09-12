"""
UniversalNavBar 插件工具模块
提供获取选中文本、上下文信息的便捷接口
"""

import os
from typing import Any, Dict, Tuple


def get_selected_text() -> str:
    """获取用户选中的文本"""
    return os.environ.get("UNB_SELECTED_TEXT", "")


def get_clipboard() -> str:
    """获取当前剪贴板内容"""
    return os.environ.get("UNB_CLIPBOARD", "")


def get_mouse_position() -> Tuple[int, int]:
    """获取触发时的鼠标位置 (x, y)"""
    x = int(os.environ.get("UNB_MOUSE_X", "0"))
    y = int(os.environ.get("UNB_MOUSE_Y", "0"))
    return (x, y)


def get_active_window() -> str:
    """获取当前活动窗口标题"""
    return os.environ.get("UNB_ACTIVE_WINDOW", "")


def get_trigger_time() -> str:
    """获取触发时间"""
    return os.environ.get("UNB_TRIGGER_TIME", "")


def get_item_id() -> str:
    """获取触发的条目 ID"""
    return os.environ.get("UNB_ITEM_ID", "")


def get_item_name() -> str:
    """获取触发的条目名称"""
    return os.environ.get("UNB_ITEM_NAME", "")


def get_config_dir() -> str:
    """获取配置文件目录"""
    return os.environ.get("UNB_CONFIG_DIR", "")


def get_plugin_dir() -> str:
    """获取插件目录"""
    return os.environ.get("UNB_PLUGIN_DIR", "")


def get_context() -> Dict[str, Any]:
    """获取完整上下文信息"""
    return {
        "selected_text": get_selected_text(),
        "clipboard": get_clipboard(),
        "mouse_position": get_mouse_position(),
        "active_window": get_active_window(),
        "trigger_time": get_trigger_time(),
        "item_id": get_item_id(),
        "item_name": get_item_name(),
        "config_dir": get_config_dir(),
        "plugin_dir": get_plugin_dir(),
    }


def has_selected_text() -> bool:
    """检查是否有选中文本"""
    return bool(get_selected_text().strip())
