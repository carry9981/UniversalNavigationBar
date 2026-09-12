# Universal Navigation Bar — 设计概览 v0.3

## 快速理解

**一句话描述：** 框选文本或按住左键 0.5 秒 → 弹出自定义导航条 → 一键执行操作

## 核心流程

```
用户框选文本 / 按住左键 0.5 秒
        │
        ▼
   ┌─────────┐
   │ 导航条  │  ← 紧邻光标显示（支持多显示器）
   │ 弹出    │
   └────┬────┘
        │
   用户点击条目
        │
        ▼
  ┌─────┼─────┐
  │     │     │
快捷键 预设文本 脚本
  │     │     │
  ▼     ▼     ▼
模拟按键 输入文本 执行脚本
```

## 技术选型

| 组件 | 选择 |
|------|------|
| 语言 | Python 3.11+ |
| GUI | PyQt6 |
| 鼠标监听 | pynput |
| **文本获取** | **Windows UI Automation API**（不复制） |
| 配置 | JSON |
| 打包 | PyInstaller |

## 三种动作类型（v1.0）

| 类型 | 说明 | 示例 |
|------|------|------|
| `hotkey` | 模拟键盘快捷键 | Ctrl+C, Ctrl+V |
| `text` | 输入预设文本 | 邮件回复模板、常用签名 |
| `script` | 运行 Python 脚本 | 搜索、翻译 |

## 插件接口（新增）

脚本可以通过三种方式获取选中文本和上下文：

| 方式 | 使用方法 | 推荐场景 |
|------|----------|----------|
| **命令行参数** | `--text "{selected_text}"` | 简单脚本 |
| **环境变量** | `os.environ["UNB_SELECTED_TEXT"]` | 多语言脚本 |
| **Python 模块** | `from unb_utils import get_selected_text` | Python 脚本（推荐） |

**示例（Python 模块方式）：**

```python
from unb_utils import get_selected_text, has_selected_text

if has_selected_text():
    text = get_selected_text()
    print(f"选中文本: {text}")
```

**环境变量列表：**
- `UNB_SELECTED_TEXT` — 选中的文本
- `UNB_CLIPBOARD` — 剪贴板内容
- `UNB_MOUSE_X` / `UNB_MOUSE_Y` — 鼠标位置
- `UNB_ACTIVE_WINDOW` — 活动窗口标题
- `UNB_TRIGGER_TIME` — 触发时间
- `UNB_ITEM_ID` / `UNB_ITEM_NAME` — 条目信息

## 已确认配置

| 配置项 | 值 |
|--------|-----|
| 管理员权限运行 | ✅ 是 |
| 脚本目录 | `./plugins/`（软件目录下） |
| 开机自启动 | ✅ 支持 |
| 多显示器 | ✅ 支持 |

## 插件目录结构

```
UniversalNavigationBar/
├── src/               # 源代码
├── plugins/           # 用户脚本（插件）
│   ├── unb_utils.py   # 插件工具模块（UNB 提供）
│   ├── search_web.py
│   └── README.md
├── config.json
└── ...
```

---

详细设计请查看 `design/design.md`
