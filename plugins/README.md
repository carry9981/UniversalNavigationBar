# UNB 插件开发说明

> 完整文档请见 **[插件开发指南](../docs/插件开发指南.md)**。本文件是快速参考。

`plugins/` 目录存放用户自定义脚本。脚本点击导航条条目后被 UNB 调用执行。

## 添加一个脚本插件（无需改源码）

1. 把脚本放进 `plugins/`，例如 `plugins/hello.py`
2. 在 `config.json` 的 `items` 里加一条：

```json
{
  "id": "my_hello",
  "name": "Hello",
  "icon": "🚀",
  "type": "script",
  "enabled": true,
  "order": 20,
  "config": {
    "script": "hello.py",
    "args": [],
    "timeout_sec": 30,
    "run_async": true
  }
}
```

3. 托盘 →「🔄 重新加载配置」生效。

## 三种获取上下文的方式

### 1. Python 模块（推荐）

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unb_utils import get_selected_text, has_selected_text

if has_selected_text():
    text = get_selected_text()
    print(text)
```

### 2. 环境变量

UNB 调用脚本时会自动设置以下环境变量（即使为空也会设置）：

| 环境变量 | 说明 |
|----------|------|
| `UNB_SELECTED_TEXT` | 选中的文本 |
| `UNB_CLIPBOARD` | 剪贴板内容 |
| `UNB_MOUSE_X` / `UNB_MOUSE_Y` | 鼠标位置 |
| `UNB_ACTIVE_WINDOW` | 活动窗口标题 |
| `UNB_TRIGGER_TIME` | 触发时间 |
| `UNB_ITEM_ID` / `UNB_ITEM_NAME` | 条目信息 |
| `UNB_CONFIG_DIR` | 配置目录 |
| `UNB_PLUGIN_DIR` | 插件目录 |

### 3. 命令行参数

在条目配置中通过 `args` 传递参数，支持变量占位符：

```json
{
  "type": "script",
  "config": {
    "script": "my_script.py",
    "args": ["--text", "{selected_text}", "--x", "{mouse_x}"]
  }
}
```

## 变量占位符

| 占位符 | 替换为 |
|--------|--------|
| `{selected_text}` | 选中的文本 |
| `{clipboard}` | 剪贴板内容 |
| `{date}` | 当前日期 `YYYY-MM-DD` |
| `{time}` | 当前时间 `HH:MM:SS` |
| `{newline}` | 换行符 |
| `{mouse_x}` / `{mouse_y}` | 鼠标坐标 |
| `{active_window}` | 活动窗口标题 |

## 注意事项

1. 选中文本可能为空（右键触发、部分软件不支持 UIA），脚本应做好空值检查
2. 脚本由 `python` 解释器执行，可依赖已安装的第三方库
3. 超时时间通过条目配置的 `timeout_sec` 控制，0 表示不限
