# Universal Navigation Bar (UNB)

Windows 桌面常驻工具：框选文本或按住鼠标左键约 0.5 秒，光标旁弹出自定义导航条，一键执行操作（快捷键 / 预设文本 / Python 脚本）。

## 功能特性

- 全局可用：任意软件（浏览器、编辑器、资源管理器）中均可触发
- 两种触发方式：框选文本、按住左键 0.5 秒
- 三种动作类型：快捷键、预设文本、Python 脚本
- 通过 Windows UI Automation 获取选中文本，不污染剪贴板
- 多显示器支持、深色主题、开机自启动、系统托盘

## 快速开始

```bash
pip install -r requirements.txt
python -m src.main
```

> 建议以管理员权限运行，以便捕获管理员权限窗口的输入事件。

## 使用方式

1. 在任意软件中框选一段文本 → 光标旁弹出导航条
2. 按住鼠标左键约 0.5 秒（不拖动）→ 光标旁弹出导航条
3. 点击条目执行对应动作，点击外部区域或按 ESC 关闭

## 配置与条目管理

**无需修改源码**，所有条目（快捷键 / 文本 / 脚本）都由 `config.json` 驱动。

配置文件位置按优先级：

1. 环境变量 `UNB_CONFIG_DIR` 指定目录
2. **程序根目录的 `config.json`（便携模式，推荐）** —— 存在即使用它
3. `%APPDATA%\UniversalNavBar\config.json`

因此：直接编辑程序目录下的 `config.json` 增删条目，再点托盘「🔄 重新加载配置」即可。

- 托盘 →「📝 管理条目…」图形界面增删改排序
- 托盘 →「⚙ 打开设置…」打开当前生效的配置文件
- 托盘 →「📂 打开配置文件夹 / 插件文件夹」

详见 **[配置指南](docs/配置指南.md)**。

## 插件开发

插件是放在 `plugins/` 目录的 Python 脚本，在 `config.json` 里加一条 `type: "script"` 条目即可调用。

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unb_utils import get_selected_text, has_selected_text

if has_selected_text():
    print(get_selected_text())
```

完整说明见 **[插件开发指南](docs/插件开发指南.md)**（含三种上下文获取方式、变量占位符、完整示例与调试技巧）。

## 项目结构

```
├── design/            # 设计文档
├── docs/              # 配置指南、插件开发指南
├── src/               # 源代码
│   ├── main.py        # 程序入口
│   ├── app.py         # 应用主类
│   ├── trigger/       # 触发模块（框选、左键长按）
│   ├── ui/            # 界面模块（导航条、托盘、编辑器）
│   ├── executor/      # 动作执行模块（快捷键、文本、脚本）
│   ├── text_getter/   # 文本获取模块（UIA + 剪贴板降级）
│   ├── config/        # 配置模块
│   └── utils/         # 工具模块
├── plugins/           # 插件脚本
├── config.json        # 配置文件（便携模式，可直接编辑）
├── requirements.txt   # 依赖
└── build.py           # 打包脚本
```

## 打包

```bash
python build.py
```

## 许可

[MIT](LICENSE)
