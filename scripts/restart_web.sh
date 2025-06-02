#!/bin/bash
# 完全重啟 ADK Web 服務

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR/.."

echo "===== 重啟 ADK Web 服務 ====="

# 殺死所有 ADK Web 服務進程
echo "停止所有現有的 ADK Web 服務進程..."
pkill -f "adk web" || true

# 等待一段時間，確保進程完全終止
echo "等待 2 秒鐘，確保所有進程已終止..."
sleep 2

# 激活虛擬環境
echo "激活 ADK 虛擬環境..."
source /Volumes/Ketomuffin_mac/AI2/A2A_agent/.venv/bin/activate

# 修復結構
echo "運行結構修復腳本..."
chmod +x ./fix_structure.sh
./fix_structure.sh

# 檢查端口 8000 是否被佔用
echo "檢查端口 8000 是否被佔用..."
if lsof -i :8000 > /dev/null; then
    echo "警告：端口 8000 已被佔用。嘗試終止相關進程..."
    lsof -i :8000 -t | xargs kill -9 || true
    sleep 2
fi

# 啟動 ADK Web 服務
echo "啟動 ADK Web 服務..."
adk web
