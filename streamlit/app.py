import streamlit as st
import os
import sys
import json
from pathlib import Path
import time
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re # 導入 re 模組
import asyncio # 導入 asyncio

# 導入 ADK 相關模組
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import Tool

# 頁面設定
st.set_page_config(
    page_title="KM股票技術分析助手",
    page_icon="📈",
    layout="wide",
)

# 標題和介紹
st.title("📊 KM股票技術分析助手")
st.markdown("輸入你想分析嘅股票代號同問題，我會提供專業技術分析 💹")

# 設置環境變數
os.environ["TIINGO_API_KEY"] = st.secrets.get("api_keys", {}).get("TIINGO_API_KEY", "2146105fde5488455a958c98755941aafb9d9c66")
# 設置 OPENROUTER_API_KEY
os.environ["OPENROUTER_API_KEY"] = st.secrets.get("api_keys", {}).get("OPENROUTER_API_KEY", "")


# 載入簡化版 MCP 工具 (這些將被包裝成 ADK 工具)
try:
    from mcp_tools.stock_tools import (
        get_stock_price,
        get_technical_indicators,
        get_momentum_analysis,
        get_volume_analysis,
        list_available_indicators
    )
except ImportError:
    try:
        from streamlit.mcp_tools.stock_tools import (
        get_stock_price,
        get_technical_indicators,
        get_momentum_analysis,
        get_volume_analysis,
        list_available_indicators
        )
    except ImportError:
        st.error("無法載入股票分析工具。請確認 mcp_tools 目錄存在。")
        st.stop()

# 使用 st.cache_resource 初始化 ADK 相關對象
@st.cache_resource
def init_adk():
    """初始化 ADK 代理和 Runner"""
    try:
        # 初始化 LiteLlm 模型
        # 使用 OPENROUTER_API_KEY，並指定模型名稱
        llm = LiteLlm(model="google/gemini-pro", api_key=os.environ.get("OPENROUTER_API_KEY"))

        # 將現有工具包裝成 ADK Tool 實例
        tools = [
            Tool(
                name="get_stock_price",
                description="獲取股票當前價格和基本信息",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "股票代碼 (例如 AAPL)"}
                    },
                    "required": ["ticker"]
                },
                function=get_stock_price
            ),
            Tool(
                name="get_technical_indicators",
                description="計算股票技術指標，例如 SMA, EMA, RSI, MACD",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "股票代碼 (例如 AAPL)"},
                        "indicators": {"type": "string", "description": "技術指標，逗號分隔 (例如 SMA,EMA,RSI,MACD)"},
                        "time_period": {"type": "string", "description": "時間範圍 (例如 90d, 180d, 1y)"}
                    },
                    "required": ["ticker", "indicators"]
                },
                function=get_technical_indicators
            ),
            Tool(
                name="get_momentum_analysis",
                description="進行股票動量分析",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "股票代碼 (例如 AAPL)"},
                        "time_period": {"type": "string", "description": "分析時間範圍 (例如 90d, 180d, 1y)"}
                    },
                    "required": ["ticker"]
                },
                function=get_momentum_analysis
            ),
             Tool(
                name="get_volume_analysis",
                description="進行股票成交量分析",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "股票代碼 (例如 AAPL)"},
                        "time_period": {"type": "string", "description": "分析時間範圍 (例如 90d, 180d, 1y)"}
                    },
                    "required": ["ticker"]
                },
                function=get_volume_analysis
            ),
             Tool(
                name="list_available_indicators",
                description="列出所有可用的技術指標",
                parameters={
                    "type": "object",
                    "properties": {}
                },
                function=list_available_indicators
            )
        ]

        # 初始化 ADK 代理
        adk_agent = Agent(
            llm=llm,
            tools=tools,
            system_message="你是一個專業的股票技術分析助手，專門回答用戶關於股票價格、技術指標、動能和成交量的問題。請根據用戶的查詢，使用提供的工具進行分析並提供詳細的回應。如果用戶沒有指定分析類型，請默認進行動能分析。如果無法識別股票代碼，請要求用戶提供有效的代碼或公司名稱。"
        )

        # 初始化 Runner
        runner = Runner(adk_agent)
        
        print("✅ ADK 代理和 Runner 初始化成功")
        return runner

    except Exception as e:
        st.error(f"初始化 ADK 失敗: {str(e)}")
        print(f"❌ 初始化 ADK 失敗: {str(e)}")
        return None

# 初始化 ADK
runner = init_adk()

# 定義處理用戶請求的函數
def process_user_query(query):
    """處理用戶查詢並生成回應"""
    if runner is None:
        return "ADK 代理初始化失敗，無法處理請求。"

    try:
        # 使用 asyncio.run() 運行異步的 runner.run()
        response = asyncio.run(runner.run(query))
        
        # runner.run() 返回的是一個 Response 對象，提取其中的文本內容
        return response.text
        
    except Exception as e:
        return f"處理請求時發生錯誤: {str(e)}"

# 生成模擬的回應流
def response_generator(response):
    words = response.split()
    for i in range(0, len(words), 3):  # 每次返回3個單詞
        chunk = " ".join(words[i:i+3])
        yield chunk + " "
        time.sleep(0.05)  # 模擬打字效果

# 初始化聊天記錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示聊天記錄
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 側邊欄 - 股票快速選擇
st.sidebar.header("快速分析")
stock_options = {
    "AAPL": "蘋果 (AAPL)",
    "TSLA": "特斯拉 (TSLA)",
    "GOOGL": "Alphabet (GOOGL)",
    "MSFT": "微軟 (MSFT)",
    "NVDA": "輝達 (NVDA)"
}

selected_stock = st.sidebar.selectbox("選擇股票:", list(stock_options.keys()), format_func=lambda x: stock_options[x])
analysis_type = st.sidebar.radio("分析類型:", ["技術指標", "動能分析", "成交量分析", "股價"])

if st.sidebar.button("執行分析"):
    if analysis_type == "技術指標":
        query = f"計算 {selected_stock} 嘅 RSI、MACD 同 SMA 技術指標"
    elif analysis_type == "動能分析":
        query = f"進行 {selected_stock} 嘅動能分析"
    elif analysis_type == "成交量分析":
        query = f"分析 {selected_stock} 嘅成交量指標"
    else:
        query = f"查詢 {selected_stock} 嘅最新股價"
    
    # 添加用戶消息
    st.session_state.messages.append({"role": "user", "content": query})
    
    # 顯示用戶消息
    with st.chat_message("user"):
        st.markdown(query)
    
    # 處理請求並顯示 AI 回應
    with st.chat_message("assistant"):
        with st.spinner("分析緊..."):
            response = process_user_query(query)
            st.markdown(response)
    
    # 添加 AI 回應到聊天記錄
    st.session_state.messages.append({"role": "assistant", "content": response})

# 處理用戶輸入
if prompt := st.chat_input("輸入你嘅問題，例如：「分析 AAPL 嘅技術指標」"):
    # 添加用戶消息到聊天記錄
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 顯示用戶消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 顯示 AI 思考中...
    with st.chat_message("assistant"):
        with st.spinner("分析緊..."):
            # 處理請求並獲取回應
            response = process_user_query(prompt)
            
            # 顯示回應
            st.write_stream(response_generator(response))
    
    # 添加 AI 回應到聊天記錄
    st.session_state.messages.append({"role": "assistant", "content": response})

# 顯示頁尾
st.markdown("---")
st.markdown("數據來源: Tiingo API | 免責聲明: 本工具僅供參考，不構成投資建議。")

# 移除簡化版提示
# st.sidebar.info("⚠️ 使用簡化版股票分析工具 (無 LLM)")
