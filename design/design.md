# Universal Navigation Bar — 设计文档

> 版本：v0.3（修订版）  
> 日期：2026-09-08  
> 状态：待评审

---

## 一、项目概述

**Universal Navigation Bar**（简称 UNB）是一个 Windows 桌面常驻工具。用户在任意软件中框选文本或长按鼠标右键后，光标旁弹出一个可自定义的导航条。点击条目即可执行对应操作（快捷键、输入预设文本、运行 Python 脚本等）。

### 核心目标

| 目标 | 说明 |
|------|------|
| 全局可用 | 在任意软件（浏览器、编辑器、资源管理器……）中均可触发 |
| 零侵入 | 不修改目标软件，通过系统级输入钩子实现 |
| 高度可定制 | 条目数量不限，内容/图标/功能均可配置 |
| 轻量常驻 | 后台内存占用 < 50 MB，CPU 空闲时接近 0% |

---

## 二、技术栈选型

| 层级 | 技术 | 理由 |
|------|------|------|
| 语言 | **Python 3.11+** | 生态丰富，快速开发，易于用户编写自定义脚本 |
| GUI 框架 | **PyQt6** | 样式灵活（QSS）、支持无边框/透明窗口 |
| 全局鼠标监听 | **pynput** | 轻量、稳定、支持全局鼠标事件 |
| 键盘模拟 | **pynput** + **pyautogui** | pynput 模拟按键，pyautogui 辅助屏幕坐标操作 |
| 文本获取 | **Windows UI Automation API** | 通过系统辅助功能接口获取选中文本，无需模拟复制 |
| 剪贴板 | **pyperclip** | 用于"输入预设文本"功能 |
| 配置格式 | **JSON** | 人可读、易于程序解析 |
| 打包分发 | **PyInstaller** 或 **Nuitka** | 生成单文件 exe，用户无需安装 Python |

---

## 三、系统架构

### 3.1 模块总览

```
┌──────────────────────────────────────────────────────────────┐
│                        UNB 主进程                             │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐     │
│  │  Trigger      │   │  NavBar UI   │   │  ConfigMgr   │     │
│  │  触发监听模块 │   │  导航条界面  │   │  配置管理器  │     │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘     │
│         │                  │                   │              │
│         └──────────────────┼───────────────────┘              │
│                            │                                  │
│                   ┌────────▼────────┐                         │
│                   │  ActionExecutor │                         │
│                   │  动作执行引擎   │                         │
│                   ├─────────────────┤                         │
│                   │ HotkeyExecutor  │  快捷键执行             │
│                   │ TextExecutor    │  预设文本输入           │
│                   │ ScriptExecutor  │  Python 脚本执行        │
│                   └─────────────────┘                         │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐     │
│  │  TrayIcon     │   │  ItemEditor  │   │  TextGetter  │     │
│  │  系统托盘     │   │  条目编辑器  │   │  文本获取器  │     │
│  └──────────────┘   └──────────────┘   └──────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 模块职责

| 模块 | 职责 | 关键接口 |
|------|------|----------|
| **Trigger** | 监听全局鼠标事件，判断是否触发导航条 | `on_trigger(callback)` |
| **NavBar UI** | 显示/隐藏导航条，渲染条目，处理点击 | `show(items, pos)`, `hide()` |
| **ConfigMgr** | 加载/保存/热重载配置文件 | `load()`, `save()`, `reload()` |
| **TextGetter** | 通过 UI Automation 获取选中文本 | `get_selected_text()` |
| **ActionExecutor** | 根据条目类型分发执行 | `execute(item, context)` |
| **HotkeyExecutor** | 模拟键盘快捷键 | `run(keys, delay)` |
| **TextExecutor** | 输入预设文本 | `run(text, mode)` |
| **ScriptExecutor** | 运行 Python 脚本 | `run(script, args, timeout)` |
| **TrayIcon** | 系统托盘图标与菜单 | `show_menu()` |
| **ItemEditor** | 条目管理 GUI | `open_editor()` |

---

## 四、选中文本获取方案（核心设计）

### 4.1 方案选择：Windows UI Automation API

**为什么不用模拟 Ctrl+C：**
- 会影响用户剪贴板内容
- 某些软件（密码框、只读区域）会阻止复制
- 用户体验不佳

**为什么选择 UI Automation：**
- 豆包、有道词典等主流软件都采用此方案
- 不影响剪贴板
- 通过系统原生辅助功能接口，兼容性好
- 可以获取任意支持 UIA 的软件中的选中文本

### 4.2 技术实现原理

```
选中文本事件
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Windows UI Automation API                              │
│                                                         │
│  1. 监听 UIA 事件：AutomationFocusChangedEvent          │
│  2. 获取当前焦点元素：FocusedElement                    │
│  3. 查询 TextPattern 接口                               │
│  4. 获取 TextPattern.DocumentRange                      │
│  5. 调用 GetSelection() 获取选中范围                    │
│  6. 读取选中范围的文本内容                              │
└─────────────────────────────────────────────────────────┘
    │
    ▼
返回选中文本
```

### 4.3 兼容性说明

| 软件类型 | 支持情况 | 说明 |
|----------|----------|------|
| 浏览器（Chrome/Edge） | ✅ 完全支持 | 网页文本可正常获取 |
| Office（Word/Excel） | ✅ 完全支持 | 文档内容可获取 |
| 记事本/文本编辑器 | ✅ 完全支持 | 原生支持 UIA |
| VS Code / IDE | ✅ 完全支持 | 代码选中可获取 |
| PDF 阅读器 | ⚠️ 部分支持 | 取决于阅读器实现 |
| 游戏/全屏应用 | ❌ 不支持 | 无法获取，但不影响触发 |

### 4.4 降级策略

如果 UI Automation 无法获取文本，提供降级方案：

```
尝试 UI Automation
    │
    ├─ 成功 → 返回文本
    │
    └─ 失败 → 尝试剪贴板方式（需用户授权）
              │
              ├─ 成功 → 返回文本，恢复原剪贴板
              │
              └─ 失败 → 返回空字符串，导航条仍显示但禁用文本相关功能
```

### 4.5 配置项

```json
{
  "text_getter": {
    "method": "uiautomation",
    "fallback_to_clipboard": true,
    "clipboard_restore": true,
    "cache_duration_ms": 500
  }
}
```

---

## 五、触发机制设计

### 5.1 触发方式一：框选文本后弹出

**原理：** 监听鼠标左键的 按下 → 移动 → 释放 完整流程，判断为"框选"后触发。

**判定逻辑：**

```
鼠标左键按下
    │
    ├─ 记录起始坐标 (x0, y0)、起始时间 t0
    │
    ▼
鼠标移动（持续监听）
    │
    ▼
鼠标左键释放
    │
    ├─ 记录结束坐标 (x1, y1)、结束时间 t1
    │
    ├─ 计算距离 d = sqrt((x1-x0)² + (y1-y0)²)
    │  计算时长 Δt = t1 - t0
    │
    ├─ 如果 d >= min_distance 且 Δt <= max_duration
    │      → 判定为"框选"
    │      → 调用 TextGetter 获取选中文本
    │      → 弹出导航条
    │
    └─ 否则 → 忽略（普通点击）
```

**配置项：**

```json
{
  "trigger": {
    "text_select": {
      "enabled": true,
      "min_distance_px": 15,
      "max_duration_sec": 2.0
    }
  }
}
```

### 5.2 触发方式二：左键长按弹出

**原理：** 监听鼠标左键按下事件，持续计时，达到阈值（且期间未拖动）后弹出导航条。若按住过程中发生拖动（超过 `move_tolerance_px`），视为普通拖拽，不触发；导航条已显示时，点击其外部区域关闭。

> 说明：v1.0 修订 —— 原「长按右键」会与目标软件的原生右键菜单冲突，故改为「长按左键」。为不影响鼠标左键原有功能，仅在「按住且未拖动」时触发。

**配置项：**

```json
{
  "trigger": {
    "left_click_hold": {
      "enabled": true,
      "hold_duration_sec": 0.5,
      "move_tolerance_px": 6
    }
  }
}
```

### 5.3 触发冲突与优先级

| 场景 | 处理方式 |
|------|----------|
| 两种触发同时满足 | 仅弹出一次，不重复 |
| 导航条已显示时再次触发 | 关闭导航条（toggle 行为） |
| 导航条显示时点击外部区域 | 关闭导航条 |
| 导航条显示时按 ESC | 关闭导航条 |
| 左键长按过程中拖动 | 不触发（视为普通拖拽） |
| 左键长按已触发后再拖动松开 | 仅弹出一次，不重复触发 |

---

## 六、导航条界面设计

### 6.1 视觉布局

```
 ┌──────────────────────────────────────────────────────┐
 │  🧭 Universal NavBar                            [×] │
 ├──────────────────────────────────────────────────────┤
 │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │
 │  │ 📋     │  │ 🔍     │  │ 📝     │  │ ⚡     │    │
 │  │ 复制   │  │ 搜索   │  │ 翻译   │  │ 格式化 │    │
 │  └────────┘  └────────┘  └────────┘  └────────┘    │
 │  ┌────────┐  ┌────────┐                              │
 │  │ 💬     │  │ ➕     │                              │
 │  │ 模板A  │  │ 更多…  │                              │
 │  └────────┘  └────────┘                              │
 └──────────────────────────────────────────────────────┘
```

### 6.2 显示规则

| 规则 | 说明 |
|------|------|
| **位置** | 紧邻鼠标光标右下方，偏移 15px |
| **边界检测** | 如果超出屏幕右/下边缘，则向左/上调整 |
| **多显示器** | 始终在当前鼠标所在的显示器上显示 |
| **最大宽度** | 400px，超过后换行 |
| **自适应高度** | 根据条目数量自动调整 |
| **置顶** | 始终显示在最上层 |
| **无焦点** | 不抢夺当前窗口焦点 |

### 6.3 多显示器支持

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  显示器 1   │  │  显示器 2   │  │  显示器 3   │
│             │  │      ▲      │  │             │
│             │  │     鼠标    │  │             │
│             │  │  ┌───────┐  │  │             │
│             │  │  │ NavBar│  │  │             │
│             │  │  └───────┘  │  │             │
└─────────────┘  └─────────────┘  └─────────────┘

导航条始终在鼠标所在的显示器上显示，
并确保不超出该显示器的边界。
```

### 6.4 视觉风格

```json
{
  "ui": {
    "theme": "dark",
    "opacity": 0.92,
    "border_radius_px": 10,
    "font_family": "Microsoft YaHei, sans-serif",
    "font_size_px": 13,
    "item_padding_px": 8,
    "max_width_px": 400,
    "position_offset_px": 15,
    "shadow": true,
    "blur_background": true
  }
}
```

**深色主题色板：**

| 元素 | 颜色 |
|------|------|
| 背景 | `#1E1E2E` |
| 文字 | `#CDD6F4` |
| 悬停背景 | `#313244` |
| 边框 | `#45475A` |
| 强调色 | `#89B4FA` |

### 6.5 交互行为

| 交互 | 行为 |
|------|------|
| 鼠标悬停条目 | 背景高亮 + 鼠标变手型 |
| 单击条目 | 执行对应动作，随后关闭导航条 |
| 点击外部区域 | 关闭导航条 |
| 按 ESC | 关闭导航条 |
| 滚轮 | 条目过多时可滚动 |

---

## 七、条目（Item）数据模型

### 7.1 条目结构

```json
{
  "id": "item_001",
  "name": "复制",
  "icon": "📋",
  "type": "hotkey",
  "enabled": true,
  "order": 0,
  "config": {
    "keys": ["ctrl", "c"]
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识符，自动生成 |
| `name` | string | 是 | 显示名称 |
| `icon` | string | 否 | Emoji 或图标路径 |
| `type` | string | 是 | 动作类型（见下文） |
| `enabled` | bool | 否 | 是否启用，默认 `true` |
| `order` | int | 否 | 排序权重，越小越靠前 |
| `config` | object | 是 | 类型专属配置（见下文） |

### 7.2 动作类型一览

| 类型 | 说明 | 版本 |
|------|------|------|
| `hotkey` | 模拟键盘快捷键 | v1.0 |
| `text` | 输入预设文本 | v1.0 |
| `script` | 运行 Python 脚本 | v1.0 |
| `click_sequence` | 执行鼠标点击序列 | 后期 |

### 7.3 动作类型：hotkey（快捷键）

```json
{
  "type": "hotkey",
  "config": {
    "keys": ["ctrl", "shift", "s"],
    "delay_ms": 50
  }
}
```

**支持的按键名：**

| 类别 | 按键 |
|------|------|
| 修饰键 | `ctrl`, `alt`, `shift`, `win` |
| 字母 | `a` - `z` |
| 数字 | `0` - `9` |
| 功能键 | `f1` - `f12` |
| 特殊键 | `enter`, `space`, `tab`, `escape`, `backspace`, `delete` |
| 方向键 | `up`, `down`, `left`, `right` |

### 7.4 动作类型：text（预设文本输入）

```json
{
  "type": "text",
  "config": {
    "content": "您好，感谢您的来信。请问有什么可以帮助您的？",
    "mode": "type",
    "delay_ms": 10,
    "variables": true
  }
}
```

| 参数 | 说明 |
|------|------|
| `content` | 要输入的文本内容 |
| `mode` | 输入方式：`type`（逐字符输入）或 `paste`（剪贴板粘贴） |
| `delay_ms` | `type` 模式下字符间隔（毫秒） |
| `variables` | 是否启用变量替换 |

**变量替换：**

| 占位符 | 替换为 |
|--------|--------|
| `{selected_text}` | 触发时选中的文本 |
| `{clipboard}` | 当前剪贴板内容 |
| `{date}` | 当前日期 `YYYY-MM-DD` |
| `{time}` | 当前时间 `HH:MM:SS` |
| `{newline}` | 换行符 |

### 7.5 动作类型：script（Python 脚本）

```json
{
  "type": "script",
  "config": {
    "script": "search_web.py",
    "args": ["--query", "{selected_text}"],
    "timeout_sec": 30,
    "run_async": false
  }
}
```

| 参数 | 说明 |
|------|------|
| `script` | 脚本文件名（相对于 `plugins/` 目录）或绝对路径 |
| `args` | 命令行参数列表，支持变量占位符 |
| `timeout_sec` | 超时时间，0 表示不限 |
| `run_async` | 是否异步执行（不阻塞 UI） |

---

## 八、插件脚本接口规范（重要新增）

### 8.1 设计目标

为插件脚本提供统一的接口，使其能够：
- 获取用户选中的文本
- 获取当前剪贴板内容
- 获取触发时的上下文信息（鼠标位置、活动窗口等）

**原则：** 接口可选使用，不强制。脚本可以通过命令行参数、环境变量或 Python 模块三种方式获取上下文。

### 8.2 接口方式一：命令行参数（推荐）

UNB 在调用脚本时，会将变量占位符替换为实际值后作为命令行参数传递。

**配置示例：**

```json
{
  "type": "script",
  "config": {
    "script": "search_web.py",
    "args": ["--text", "{selected_text}", "--x", "{mouse_x}", "--y", "{mouse_y}"]
  }
}
```

**实际执行命令：**

```bash
python plugins/search_web.py --text "用户选中的内容" --x 500 --y 300
```

**脚本接收示例：**

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--text", default="", help="选中的文本")
parser.add_argument("--x", type=int, default=0, help="鼠标X坐标")
parser.add_argument("--y", type=int, default=0, help="鼠标Y坐标")
args = parser.parse_args()

print(f"选中文本: {args.text}")
print(f"鼠标位置: ({args.x}, {args.y})")
```

### 8.3 接口方式二：环境变量

UNB 在调用脚本时，会自动设置以下环境变量。

**环境变量列表：**

| 环境变量 | 说明 | 示例值 |
|----------|------|--------|
| `UNB_SELECTED_TEXT` | 用户选中的文本 | `"Hello World"` |
| `UNB_CLIPBOARD` | 当前剪贴板内容 | `"copied text"` |
| `UNB_MOUSE_X` | 触发时鼠标 X 坐标 | `"500"` |
| `UNB_MOUSE_Y` | 触发时鼠标 Y 坐标 | `"300"` |
| `UNB_ACTIVE_WINDOW` | 当前活动窗口标题 | `"Chrome - Google"` |
| `UNB_TRIGGER_TIME` | 触发时间戳 | `"2026-09-08 14:30:00"` |
| `UNB_CONFIG_DIR` | 配置文件目录 | `"C:/Users/xxx/AppData/Roaming/UniversalNavBar"` |
| `UNB_PLUGIN_DIR` | 插件目录 | `"D:/UniversalNavigationBar/plugins"` |
| `UNB_ITEM_ID` | 触发的条目 ID | `"search_web"` |
| `UNB_ITEM_NAME` | 触发的条目名称 | `"搜索"` |

**脚本接收示例：**

```python
import os

selected_text = os.environ.get("UNB_SELECTED_TEXT", "")
mouse_x = int(os.environ.get("UNB_MOUSE_X", "0"))
mouse_y = int(os.environ.get("UNB_MOUSE_Y", "0"))
active_window = os.environ.get("UNB_ACTIVE_WINDOW", "")

if selected_text:
    print(f"检测到选中文本: {selected_text}")
else:
    print("未检测到选中文本")
```

### 8.4 接口方式三：Python 模块（unb_utils）

UNB 提供一个轻量级 Python 模块 `unb_utils.py`，放在插件目录下。脚本可以直接 import 使用。

**模块位置：** `plugins/unb_utils.py`

**模块提供的 API：**

```python
# plugins/unb_utils.py
"""
UniversalNavBar 插件工具模块
提供获取选中文本、上下文信息的便捷接口
"""

import os
from typing import Optional, Dict, Any, Tuple


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
```

**脚本使用示例：**

```python
# plugins/my_script.py
import sys
import os

# 添加插件目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unb_utils import get_selected_text, get_mouse_position, has_selected_text

def main():
    if has_selected_text():
        text = get_selected_text()
        print(f"处理选中文本: {text}")
    else:
        print("未检测到选中文本")
    
    x, y = get_mouse_position()
    print(f"触发位置: ({x}, {y})")

if __name__ == "__main__":
    main()
```

### 8.5 三种接口方式对比

| 方式 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **命令行参数** | 显式、清晰、无需额外依赖 | 参数多时命令较长 | 简单脚本、Shell 脚本 |
| **环境变量** | 不污染参数列表、支持任意语言 | 需要手动读取 | 多语言脚本 |
| **Python 模块** | API 友好、有类型提示、代码清晰 | 仅限 Python 脚本 | Python 脚本（推荐） |

**建议：** 三种方式可混合使用。UNB 会同时设置环境变量和命令行参数，脚本作者可选择最方便的方式。

### 8.6 接口使用规范

**对于脚本作者：**
1. 选中文本可能为空字符串（如右键触发、某些软件不支持 UIA）
2. 应该做好空值检查，提供合理的默认行为
3. 不要依赖选中文本一定存在

**UNB 保证：**
1. 所有环境变量都会设置，即使值为空字符串
2. 命令行参数中的变量占位符会被替换，空值替换为空字符串
3. `unb_utils.py` 模块始终可用，返回空字符串作为默认值

### 8.7 完整示例脚本

**示例 1：搜索选中文本**

```python
#!/usr/bin/env python3
"""
UNB 插件：在浏览器中搜索选中的文本
如果未选中文本，则打开搜索引擎首页
"""

import sys
import os
import webbrowser
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unb_utils import get_selected_text, has_selected_text


def main():
    if has_selected_text():
        text = get_selected_text()
        encoded = urllib.parse.quote(text)
        url = f"https://www.google.com/search?q={encoded}"
    else:
        url = "https://www.google.com"
    
    print(f"打开: {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    main()
```

**示例 2：翻译选中文本（调用 API）**

```python
#!/usr/bin/env python3
"""
UNB 插件：翻译选中的文本
"""

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unb_utils import get_selected_text, has_selected_text


def translate_text(text: str, target_lang: str = "zh") -> str:
    """调用翻译 API（示例）"""
    # 这里替换为实际的翻译 API
    url = "https://api.example.com/translate"
    payload = {"text": text, "target": target_lang}
    
    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        return resp.json().get("translated", text)
    except Exception as e:
        return f"翻译失败: {e}"


def main():
    if not has_selected_text():
        print("错误：未检测到选中文本")
        print("请先选中要翻译的文本，然后重试")
        sys.exit(1)
    
    text = get_selected_text()
    print(f"原文: {text}")
    
    translated = translate_text(text)
    print(f"译文: {translated}")


if __name__ == "__main__":
    main()
```

**示例 3：插入当前日期时间**

```python
#!/usr/bin/env python3
"""
UNB 插件：将当前日期时间输出
不依赖选中文本
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unb_utils import get_item_name


def main():
    item_name = get_item_name()
    now = datetime.now()
    
    # 根据条目名称决定格式
    if "日期" in item_name:
        result = now.strftime("%Y-%m-%d")
    elif "时间" in item_name:
        result = now.strftime("%H:%M:%S")
    else:
        result = now.strftime("%Y-%m-%d %H:%M:%S")
    
    print(result)


if __name__ == "__main__":
    main()
```

---

## 九、配置文件完整结构

**文件位置：** `%APPDATA%/UniversalNavBar/config.json`

> v1.0 修订：支持**便携模式**——若程序根目录存在 `config.json`，则优先使用它。
> 这样用户可直接编辑程序目录的配置文件来增删条目/脚本，无需修改源码。
> 优先级：`UNB_CONFIG_DIR` 环境变量 > 程序根目录 `config.json` > `%APPDATA%/UniversalNavBar/config.json`。

```json
{
  "version": "1.0.0",
  "trigger": {
    "text_select": {
      "enabled": true,
      "min_distance_px": 15,
      "max_duration_sec": 2.0
    },
    "left_click_hold": {
      "enabled": true,
      "hold_duration_sec": 0.5,
      "move_tolerance_px": 6
    }
  },
  "text_getter": {
    "method": "uiautomation",
    "fallback_to_clipboard": true,
    "clipboard_restore": true,
    "cache_duration_ms": 500
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
    "shadow": true,
    "blur_background": true
  },
  "items": [
    {
      "id": "builtin_copy",
      "name": "复制",
      "icon": "📋",
      "type": "hotkey",
      "enabled": true,
      "order": 0,
      "config": {
        "keys": ["ctrl", "c"],
        "delay_ms": 50
      }
    },
    {
      "id": "builtin_search",
      "name": "搜索",
      "icon": "🔍",
      "type": "script",
      "enabled": true,
      "order": 1,
      "config": {
        "script": "search_web.py",
        "args": ["{selected_text}"],
        "timeout_sec": 10,
        "run_async": true
      }
    },
    {
      "id": "builtin_greeting",
      "name": "问候语",
      "icon": "👋",
      "type": "text",
      "enabled": true,
      "order": 2,
      "config": {
        "content": "您好，请问有什么可以帮助您的？",
        "mode": "type",
        "delay_ms": 10,
        "variables": false
      }
    }
  ],
  "general": {
    "auto_start": true,
    "check_updates": true
  }
}
```

---

## 十、条目管理方案

### 10.1 管理入口

| 方式 | 适合场景 | 说明 |
|------|----------|------|
| **系统托盘菜单** | 快速操作 | 右键托盘图标 → "管理条目" |
| **管理窗口 GUI** | 可视化编辑 | 完整的增删改查界面 |
| **直接编辑 JSON** | 高级用户 | 用任意编辑器打开 config.json |

### 10.2 系统托盘菜单

```
┌───────────────────────────┐
│  🧭 Universal NavBar      │
├───────────────────────────┤
│  ✅ 已启用                │
│  ─────────────────────── │
│  📝 管理条目…             │
│  ⚙ 打开设置…             │
│  📂 打开配置文件夹        │
│  📂 打开插件文件夹        │
│  ─────────────────────── │
│  🔄 重新加载配置          │
│  🚀 开机自启动    [✓]   │
│  ─────────────────────── │
│  ❌ 退出                  │
└───────────────────────────┘
```

### 10.3 条目管理窗口

```
┌──────────────────────────────────────────────────────────┐
│  📝 条目管理                                    [×]      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ☑ 📋 复制              hotkey    [↑][↓][✏][🗑]  │   │
│  │  ☑ 🔍 搜索              script    [↑][↓][✏][🗑]  │   │
│  │  ☑ 👋 问候语            text      [↑][↓][✏][🗑]  │   │
│  │  …                                               │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────────┐  │
│  │ ➕ 添加 │  │ 📥 导入 │  │ 📤 导出 │  │ 💾 保存更改 │  │
│  └────────┘  └────────┘  └────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 十一、项目目录结构

```
UniversalNavigationBar/                # 软件根目录（当前目录）
│
├── design/                            # 设计文档
│   ├── design.md                      # 完整设计文档（本文件）
│   └── overview.md                    # 快速概览
│
├── src/                               # 源代码
│   ├── main.py                        # 程序入口
│   ├── app.py                         # 应用主类
│   │
│   ├── trigger/                       # 触发模块
│   │   ├── __init__.py
│   │   ├── base.py                    # 触发器基类
│   │   ├── text_select.py             # 框选文本触发
│   │   └── left_click_hold.py         # 左键长按触发
│   │
│   ├── ui/                            # 界面模块
│   │   ├── __init__.py
│   │   ├── navbar.py                  # 导航条窗口
│   │   ├── item_widget.py             # 单个条目组件
│   │   ├── tray_icon.py               # 系统托盘
│   │   ├── editor_window.py           # 条目管理窗口
│   │   ├── item_dialog.py             # 添加/编辑对话框
│   │   ├── styles.py                  # 主题样式
│   │   └── multi_monitor.py           # 多显示器支持
│   │
│   ├── executor/                      # 动作执行模块
│   │   ├── __init__.py
│   │   ├── base.py                    # 执行器基类
│   │   ├── hotkey_executor.py         # 快捷键执行
│   │   ├── text_executor.py           # 预设文本输入
│   │   ├── script_executor.py         # 脚本执行
│   │   └── click_executor.py          # 点击序列（后期）
│   │
│   ├── text_getter/                   # 文本获取模块
│   │   ├── __init__.py
│   │   ├── base.py                    # 获取器基类
│   │   ├── uia_getter.py              # UI Automation 方式
│   │   └── clipboard_getter.py        # 剪贴板降级方式
│   │
│   ├── config/                        # 配置模块
│   │   ├── __init__.py
│   │   ├── manager.py                 # 配置管理器
│   │   ├── models.py                  # 数据模型
│   │   └── defaults.py                # 默认配置
│   │
│   └── utils/                         # 工具模块
│       ├── __init__.py
│       ├── clipboard.py               # 剪贴板工具
│       └── variables.py               # 变量替换
│
├── plugins/                           # 插件目录（用户自定义脚本）
│   ├── unb_utils.py                   # 插件工具模块（UNB 提供）
│   ├── search_web.py                  # 示例：搜索选中文本
│   ├── translate.py                   # 示例：翻译
│   └── README.md                      # 插件开发说明
│
├── resources/                         # 资源文件
│   ├── icons/
│   └── tray_icon.ico
│
├── config.json                        # 配置文件
├── requirements.txt                   # Python 依赖
├── build.py                           # 打包脚本
├── install.bat                        # 安装/注册开机启动
├── uninstall.bat                      # 卸载/取消开机启动
├── README.md                          # 项目说明
└── LICENSE                            # 开源协议
```

---

## 十二、开机自启动

### 12.1 实现方式

通过 Windows 注册表实现开机自启动：

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

### 12.2 配置项

```json
{
  "general": {
    "auto_start": true
  }
}
```

---

## 十三、关键实现细节

### 13.1 全局钩子的权限

- Windows 上 `pynput` 使用 `ctypes` 调用 `SetWindowsHookEx`
- 如果目标软件以管理员身份运行，钩子无法捕获其事件
- **解决方案：** 默认以管理员权限运行 UNB

### 13.2 性能优化

| 策略 | 说明 |
|------|------|
| 延迟加载 | 导航条 UI 仅在首次触发时创建 |
| 事件过滤 | 鼠标移动事件做节流（throttle），每 16ms 最多处理一次 |
| 懒执行 | 脚本仅在点击时启动，不预加载 |
| 内存管理 | 导航条关闭后释放非必要资源 |

---

## 十四、开发计划

| 阶段 | 周期 | 交付物 |
|------|------|--------|
| **P1 基础框架** | 第 1 周 | 项目骨架、配置加载、系统托盘、开机自启动 |
| **P2 触发机制** | 第 2 周 | 框选触发 + 左键长按触发 |
| **P3 文本获取** | 第 2 周 | UI Automation 文本获取 + 降级方案 |
| **P4 导航条 UI** | 第 3 周 | 导航条显示、条目渲染、多显示器支持 |
| **P5 动作执行** | 第 4 周 | 快捷键 + 预设文本 + 脚本执行 + 插件接口 |
| **P6 条目管理** | 第 5 周 | 管理窗口、添加/编辑/删除、导入导出 |
| **P7 打磨发布** | 第 6 周 | 测试、打包、文档、安装脚本 |

---

## 十五、配置摘要

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `trigger.text_select.enabled` | `true` | 启用框选触发 |
| `trigger.text_select.min_distance_px` | `15` | 最小拖动距离 |
| `trigger.left_click_hold.hold_duration_sec` | `0.5` | 长按阈值 |
| `text_getter.method` | `uiautomation` | 文本获取方式 |
| `text_getter.fallback_to_clipboard` | `true` | 失败时降级到剪贴板 |
| `ui.theme` | `dark` | 主题 |
| `ui.opacity` | `0.92` | 不透明度 |
| `ui.max_width_px` | `400` | 导航条最大宽度 |
| `general.auto_start` | `true` | 开机自启动 |

---

*文档版本：v0.3*  
*最后更新：2026-09-08*  
*等待评审反馈后进入开发阶段。*
