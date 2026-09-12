"""配置管理器：负责配置的加载、保存、热重载与默认值填充。"""
from __future__ import annotations

import json
import os
import sys
import threading
from typing import Optional

from .defaults import APP_NAME, default_config
from .models import ConfigError, Item


def get_app_root() -> str:
    """程序根目录（打包后为 exe 所在目录，开发时为项目根目录）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def resolve_config_dir(app_root: Optional[str] = None) -> str:
    """确定配置目录。

    优先便携模式：若程序目录下存在 ``config.json``，则直接使用程序目录，
    这样用户只改程序目录里的 ``config.json`` 即可增删条目，无需动源码。
    否则回退到 ``%APPDATA%/UniversalNavBar``。
    """
    root = app_root or get_app_root()
    if os.path.exists(os.path.join(root, "config.json")):
        return root
    return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)


def _deep_merge(base: dict, override: dict) -> dict:
    """递归合并配置，override 优先。"""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    """管理配置文件与条目。"""

    def __init__(self, config_dir: Optional[str] = None) -> None:
        # 配置目录优先级：显式参数 > 环境变量 > 便携模式/APPDATA
        if config_dir:
            self.config_dir = config_dir
        else:
            self.config_dir = os.environ.get("UNB_CONFIG_DIR") or resolve_config_dir()
        self.config_path = os.path.join(self.config_dir, "config.json")
        self._data: dict = {}
        self._lock = threading.RLock()
        first_run = not os.path.exists(self.config_path)
        self.load()
        if first_run:
            # 首次运行：将默认配置落盘，方便用户直接编辑/打开
            self.save()

    # ------------------------------------------------------------------ 基础
    def load(self) -> dict:
        """从磁盘加载配置；不存在或损坏时回退到默认配置。"""
        with self._lock:
            data = default_config()
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                    if isinstance(raw, dict):
                        data = _deep_merge(data, raw)
                except (json.JSONDecodeError, OSError) as exc:
                    print(f"[config] 加载配置失败，使用默认配置: {exc}")
            self._data = data
            return data

    def reload(self) -> dict:
        """热重载配置。"""
        return self.load()

    def save(self) -> None:
        """保存当前配置到磁盘。"""
        with self._lock:
            os.makedirs(self.config_dir, exist_ok=True)
            tmp_path = self.config_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.config_path)

    # ------------------------------------------------------------------ 访问
    def get(self, *keys, default=None):
        """按路径读取配置，例如 get("trigger", "text_select", "enabled")。"""
        node = self._data
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def set(self, value, *keys) -> None:
        """按路径写入配置。"""
        with self._lock:
            if not keys:
                raise ValueError("set 需要至少一个 key")
            node = self._data
            for key in keys[:-1]:
                node = node.setdefault(key, {})
                if not isinstance(node, dict):
                    raise ValueError(f"路径 {keys} 中 {key} 不是对象")
            node[keys[-1]] = value

    @property
    def data(self) -> dict:
        return self._data

    # ------------------------------------------------------------------ 条目
    def get_items(self, enabled_only: bool = True) -> list[Item]:
        """返回按 order 排序的条目列表。"""
        raw_items = self._data.get("items", [])
        items: list[Item] = []
        for raw in raw_items:
            try:
                item = Item.from_dict(raw)
            except ConfigError as exc:
                print(f"[config] 忽略无效条目: {exc}")
                continue
            if enabled_only and not item.enabled:
                continue
            items.append(item)
        items.sort(key=lambda it: (it.order, it.id))
        return items

    def all_items(self) -> list[Item]:
        """返回全部条目（含禁用），用于编辑器。"""
        return self.get_items(enabled_only=False)

    def set_items(self, items: list[Item]) -> None:
        """整体覆盖条目列表。"""
        with self._lock:
            self._data["items"] = [it.to_dict() for it in items]

    def add_item(self, item: Item) -> None:
        with self._lock:
            self._data.setdefault("items", []).append(item.to_dict())

    def update_item(self, item: Item) -> bool:
        """按 id 更新条目；不存在则返回 False。"""
        with self._lock:
            items = self._data.setdefault("items", [])
            for i, raw in enumerate(items):
                if raw.get("id") == item.id:
                    items[i] = item.to_dict()
                    return True
            return False

    def remove_item(self, item_id: str) -> bool:
        with self._lock:
            items = self._data.setdefault("items", [])
            for i, raw in enumerate(items):
                if raw.get("id") == item_id:
                    items.pop(i)
                    return True
            return False
