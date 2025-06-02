#!/bin/bash
# 程序目錄文件結構自檢和修復工具

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

echo "===== ADK Tool Agent 結構自檢 ====="

# 檢查 ADK 是否正確安裝和激活
source /Volumes/Ketomuffin_mac/AI2/A2A_agent/.venv/bin/activate

# 檢查 agent.py 是否存在
if [ ! -f "agent.py" ]; then
    echo "創建 agent.py..."
    cat > agent.py << 'EOF'
"""
一個簡單的模塊，用於將 root_agent 暴露給 ADK CLI
"""

# 從 tool_agent 包導入 root_agent
try:
    from tool_agent.agent.agent import root_agent
except ImportError as e:
    print(f"錯誤: 無法導入 root_agent: {e}")
    # 創建一個虛擬的 root_agent，以便 ADK CLI 可以加載
    import google.adk.agents
    
    class DummyRootAgent:
        def __init__(self):
            print("加載了虛擬的 root_agent。實際的代理可能未正確初始化。")
            
    root_agent = DummyRootAgent()
EOF
fi

# 確保 tool_agent/agent 目錄存在
mkdir -p tool_agent/agent

# 確保 tool_agent/__init__.py 正確
cat > tool_agent/__init__.py << 'EOF'
"""
Tool Agent 套件初始化文件
"""
# 版本信息
__version__ = "0.1.0"

# 導入 agent 模塊供 ADK 使用
try:
    from . import agent
except ImportError:
    print("警告: 無法導入 agent 子模塊")
EOF

# 確保 tool_agent/agent/__init__.py 正確
cat > tool_agent/agent/__init__.py << 'EOF'
"""
tool_agent.agent 子模塊
"""
# 從 agent.py 導入 root_agent
try:
    from .agent import root_agent
except ImportError:
    print("警告: 無法從 agent.py 導入 root_agent")
EOF

# 確保工具目錄存在
mkdir -p tool_agent/tools

# 檢查 tool_agent/agent/agent.py 文件是否存在
if [ ! -f "tool_agent/agent/agent.py" ]; then
    echo "確保 tool_agent/agent/agent.py 存在..."
    
    # 如果舊的 agent.py 存在，複製它
    if [ -f "tool_agent/agent.py" ]; then
        echo "發現舊的 agent.py，正在複製..."
        cp tool_agent/agent.py tool_agent/agent/agent.py
    fi
fi

# 檢查 Python 路徑和模塊導入
echo "測試 Python 路徑和模塊導入..."
python -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); try: from tool_agent.agent import root_agent; print('✅ 成功導入 root_agent'); except Exception as e: print(f'❌ 導入 root_agent 失敗: {e}')"

# 嘗試在當前進程中執行 ADK
echo "嘗試獲取 ADK 應用列表..."
adk list-apps

echo ""
echo "===== 自檢完成 ====="
echo "如果上面沒有錯誤，請嘗試啟動 ADK Web 服務:"
echo "./start_web.sh"
