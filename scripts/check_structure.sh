#!/bin/bash
# 檢查 Tool Agent 結構

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

echo "===== Tool Agent 結構檢查 ====="

# 檢查目錄結構
if [ -d "tool_agent/agent" ]; then
    echo "✅ tool_agent/agent 目錄存在"
else
    echo "❌ tool_agent/agent 目錄不存在"
fi

if [ -f "tool_agent/agent/agent.py" ]; then
    echo "✅ tool_agent/agent/agent.py 文件存在"
else
    echo "❌ tool_agent/agent/agent.py 文件不存在"
fi

if [ -f "tool_agent/agent/__init__.py" ]; then
    echo "✅ tool_agent/agent/__init__.py 文件存在"
else
    echo "❌ tool_agent/agent/__init__.py 文件不存在"
fi

if [ -f "tool_agent/__init__.py" ]; then
    echo "✅ tool_agent/__init__.py 文件存在"
else
    echo "❌ tool_agent/__init__.py 文件不存在"
fi

# 檢查文件內容
echo ""
echo "===== 檢查文件內容 ====="

if grep -q "from . import agent" "tool_agent/__init__.py"; then
    echo "✅ tool_agent/__init__.py 正確導入 agent 模塊"
else
    echo "❌ tool_agent/__init__.py 未正確導入 agent 模塊"
fi

if grep -q "from .agent import root_agent" "tool_agent/agent/__init__.py"; then
    echo "✅ tool_agent/agent/__init__.py 正確導出 root_agent"
else
    echo "❌ tool_agent/agent/__init__.py 未正確導出 root_agent"
fi

if grep -q "root_agent = Agent" "tool_agent/agent/agent.py"; then
    echo "✅ tool_agent/agent/agent.py 定義了 root_agent"
else
    echo "❌ tool_agent/agent/agent.py 未定義 root_agent"
fi

echo ""
echo "===== Python 模塊導入測試 ====="
# 嘗試使用 Python 導入 root_agent
python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); from tool_agent.agent import root_agent; print('✅ 成功導入 root_agent')" 2>/dev/null || echo "❌ 無法導入 root_agent"

echo ""
echo "如果以上所有檢查都通過，則應該可以正常運行 ADK Web 服務。"
echo "使用 ./start_web.sh 啟動 ADK Web 服務。"
