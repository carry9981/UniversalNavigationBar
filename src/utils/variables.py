"""变量替换工具。"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Mapping

_VARIABLE_PATTERN = re.compile(r"\{(\w+)\}")


def _default_value(name: str, variables: Mapping) -> str:
    if name == "date":
        return datetime.now().strftime("%Y-%m-%d")
    if name == "time":
        return datetime.now().strftime("%H:%M:%S")
    if name == "newline":
        return "\n"
    return ""


def replace_variables(text: str, variables: Mapping, enabled: bool = True) -> str:
    """替换文本中的变量占位符。

    :param text: 含有 ``{var}`` 占位符的文本
    :param variables: 变量名到值的映射（见 Context.as_mapping）
    :param enabled: 是否启用变量替换
    """
    if not enabled or not text:
        return text

    def _repl(match: re.Match) -> str:
        name = match.group(1)
        if name in variables:
            value = variables[name]
            return "" if value is None else str(value)
        return _default_value(name, variables)

    return _VARIABLE_PATTERN.sub(_repl, text)
