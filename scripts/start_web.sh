#!/bin/bash
# 使用正確的虛擬環境啟動 ADK Web 服務

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR/.."

echo "===== 啟動 ADK Web 服務 ====="
echo "請在瀏覽器中訪問 http://localhost:8000"
echo ""

# 啟用正確的虛擬環境
source /Volumes/Ketomuffin_mac/AI2/A2A_agent/.venv/bin/activate

# 啟動 ADK Web 服務
adk web
