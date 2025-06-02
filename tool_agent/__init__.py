# tool_agent/__init__.py
# 呢個檔案令 'tool_agent' 成為一個 Python package
# 佢導入 agent 實例嚟令佢可以被發現

from .agent import root_agent

__all__ = ['root_agent']
