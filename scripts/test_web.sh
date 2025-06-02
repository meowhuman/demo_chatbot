#!/bin/bash
# 測試正在運行的 ADK Web 服務

echo "發送請求到 http://localhost:8000/list-apps..."
curl -s http://localhost:8000/list-apps | grep -q "tool_agent" && echo "✅ 找到 tool_agent 應用程序" || echo "❌ 未找到 tool_agent 應用程序"

echo ""
echo "訪問 http://localhost:8000，確認 ADK Web 界面可以正常顯示。"
echo "如果一切正常，您可以繼續使用 ADK Web 服務。"
