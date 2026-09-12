"""数据模型。"""
from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

VALID_ITEM_TYPES = {"hotkey", "text", "script", "click_sequence"}

VALID_TEXT_MODES = {"type", "paste"}


class ConfigError(ValueError):
    """配置错误。"""


@dataclass
class Item:
    """导航条条目。"""

    name: str
    type: str
    config: dict
    icon: str = ""
    enabled: bool = True
    order: int = 0
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    # 兼容旧字段名 ``type``（python 内置名的 shadow 无副作用，仅为可读性）。
    @property
    def item_type(self) -> str:
        return self.type

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        if not isinstance(data, dict):
            raise ConfigError(f"条目必须是对象，得到 {type(data).__name__}")
        name = data.get("name")
        if not name:
            raise ConfigError("条目缺少必填字段 name")
        item_type = data.get("type")
        if item_type not in VALID_ITEM_TYPES:
            raise ConfigError(f"条目 '{name}' 的 type '{item_type}' 无效")
        config = data.get("config")
        if not isinstance(config, dict):
            raise ConfigError(f"条目 '{name}' 缺少 config 对象")

        item = cls(
            id=str(data.get("id") or uuid.uuid4().hex[:12]),
            name=str(name),
            icon=str(data.get("icon") or ""),
            type=str(item_type),
            enabled=bool(data.get("enabled", True)),
            order=int(data.get("order", 0)),
            config=copy.deepcopy(config),
        )
        item.validate()
        return item

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "type": self.type,
            "enabled": self.enabled,
            "order": self.order,
            "config": copy.deepcopy(self.config),
        }

    def validate(self) -> None:
        """校验条目配置的完整性。"""
        if self.type not in VALID_ITEM_TYPES:
            raise ConfigError(f"条目 '{self.name}' 的 type '{self.type}' 无效")
        cfg = self.config or {}
        if self.type == "hotkey":
            keys = cfg.get("keys")
            if not isinstance(keys, list) or not keys:
                raise ConfigError(f"hotkey 条目 '{self.name}' 缺少 keys 列表")
        elif self.type == "text":
            if "content" not in cfg:
                raise ConfigError(f"text 条目 '{self.name}' 缺少 content")
            mode = cfg.get("mode", "type")
            if mode not in VALID_TEXT_MODES:
                raise ConfigError(f"text 条目 '{self.name}' 的 mode '{mode}' 无效")
        elif self.type == "script":
            if not cfg.get("script"):
                raise ConfigError(f"script 条目 '{self.name}' 缺少 script 文件名")


@dataclass
class Context:
    """触发上下文，传递给执行器与插件脚本。"""

    selected_text: str = ""
    clipboard: str = ""
    mouse_x: int = 0
    mouse_y: int = 0
    active_window: str = ""
    trigger_time: str = ""
    item_id: str = ""
    item_name: str = ""
    trigger_source: str = ""
    config_dir: str = ""
    plugin_dir: str = ""

    def to_env(self) -> dict:
        """转换为插件脚本的环境变量字典。"""
        return {
            "UNB_SELECTED_TEXT": self.selected_text,
            "UNB_CLIPBOARD": self.clipboard,
            "UNB_MOUSE_X": str(self.mouse_x),
            "UNB_MOUSE_Y": str(self.mouse_y),
            "UNB_ACTIVE_WINDOW": self.active_window,
            "UNB_TRIGGER_TIME": self.trigger_time,
            "UNB_ITEM_ID": self.item_id,
            "UNB_ITEM_NAME": self.item_name,
            "UNB_CONFIG_DIR": self.config_dir,
            "UNB_PLUGIN_DIR": self.plugin_dir,
        }

    def as_mapping(self) -> dict:
        """转换为变量替换使用的映射。"""
        return {
            "selected_text": self.selected_text,
            "clipboard": self.clipboard,
            "mouse_x": str(self.mouse_x),
            "mouse_y": str(self.mouse_y),
            "active_window": self.active_window,
            "trigger_time": self.trigger_time,
            "item_id": self.item_id,
            "item_name": self.item_name,
        }
