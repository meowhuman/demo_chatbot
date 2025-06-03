#!/bin/bash
# 在本地運行 Streamlit 應用進行測試

# 切換到 Streamlit 應用目錄
cd /Volumes/Ketomuffin_mac/ADK/agent-development-kit/KM-stock-ta-streamlit

# 確保已安裝依賴項
echo "檢查依賴項..."
pip install -r requirements.txt

# 運行應用
echo "啟動 Streamlit 應用..."
streamlit run app.py

# 注意: 此腳本將會阻塞終端，直到 Streamlit 應用被終止
# 可以使用 Ctrl+C 來停止應用
