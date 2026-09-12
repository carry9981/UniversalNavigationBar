#!/usr/bin/env python3
"""
UNB 插件：在浏览器中搜索选中的文本
如果未选中文本，则打开搜索引擎首页
"""

import os
import sys
import urllib.parse
import webbrowser

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
