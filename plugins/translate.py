#!/usr/bin/env python3
"""
UNB 插件：翻译选中的文本
通过有道在线翻译（无需 API key），未选中文本时提示
"""

import os
import sys
import urllib.parse
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unb_utils import get_selected_text, has_selected_text


def main():
    if not has_selected_text():
        print("错误：未检测到选中文本")
        print("请先选中要翻译的文本，然后重试")
        sys.exit(1)

    text = get_selected_text()
    encoded = urllib.parse.quote(text)
    url = f"https://fanyi.youdao.com/#/TextTranslate?text={encoded}"
    print(f"翻译: {text[:50]}")
    webbrowser.open(url)


if __name__ == "__main__":
    main()
