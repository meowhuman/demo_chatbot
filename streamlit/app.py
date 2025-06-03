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

# 載入簡化版 MCP 工具
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

# 定義處理用戶請求的函數
def process_user_query(query):
    """處理用戶查詢並生成回應"""
    try:
        query_lower = query.lower()
        
        # 提取股票代碼 (使用正則表達式)
        ticker = None
        # 匹配 1 到 5 個大寫字母或數字的組合
        match = re.search(r'[A-Z0-9]{1,5}', query.upper())
        if match:
            ticker = match.group(0)

        # 如果沒找到，嘗試通過常見公司名稱
        if not ticker:
            common_names = {
                "apple": "AAPL",
                "蘋果": "AAPL",
                "microsoft": "MSFT",
                "微軟": "MSFT",
                "google": "GOOGL",
                "谷歌": "GOOGL",
                "amazon": "AMZN",
                "亞馬遜": "AMZN",
                "tesla": "TSLA",
                "特斯拉": "TSLA",
                "facebook": "META",
                "臉書": "META",
                "nvidia": "NVDA",
                "輝達": "NVDA"
            }

            for name, symbol in common_names.items():
                if name in query_lower:
                    ticker = symbol
                    break

        if not ticker:
            return "請提供有效的股票代碼或公司名稱，例如 AAPL 或 蘋果。"
            
        # 決定分析類型
        if "股價" in query_lower or "價格" in query_lower or "price" in query_lower:
            result = get_stock_price(ticker)
            if "error" in result:
                return f"獲取 {ticker} 股價時發生錯誤: {result['error']}"

            # 確保所有需要的鍵都存在
            if not all(k in result for k in ["company_name", "ticker", "current_price", "open_price", "high_price", "low_price", "volume", "date"]):
                 return f"獲取 {ticker} 股價時返回的數據格式不正確。"

            response = f"**{result['company_name']} ({result['ticker']})** 股票分析 📊\n\n"
            response += f"目前價格: ${result['current_price']:.2f}\n"
            response += f"今日開盤: ${result['open_price']:.2f}\n"
            response += f"今日最高: ${result['high_price']:.2f}\n"
            response += f"今日最低: ${result['low_price']:.2f}\n"
            response += f"成交量: {result['volume']:,}\n"
            response += f"日期: {result['date']}\n\n"
            response += "⚠️ 風險提醒: 投資有風險，入市需謹慎。過往表現不代表未來結果。"

            return response
            
        elif "技術指標" in query_lower or "technical" in query_lower or "indicator" in query_lower:
            indicators = "SMA,EMA,RSI,MACD"  # 預設指標
            
            # 檢查是否有特定指標請求
            indicator_keywords = {
                "sma": "SMA", 
                "ema": "EMA", 
                "rsi": "RSI", 
                "macd": "MACD",
                "移動平均": "SMA,EMA",
                "相對強弱": "RSI"
            }
            
            requested_indicators = []
            for keyword, ind in indicator_keywords.items():
                if keyword in query_lower:
                    requested_indicators.extend(ind.split(","))
            
            if requested_indicators:
                indicators = ",".join(set(requested_indicators))
                
            # 決定時間範圍
            time_period = "365d"  # 預設時間
            if "月" in query_lower or "month" in query_lower:
                if "一個月" in query_lower or "1個月" in query_lower or "1 month" in query_lower:
                    time_period = "30d"
                elif "三個月" in query_lower or "3個月" in query_lower or "3 month" in query_lower:
                    time_period = "90d"
                elif "六個月" in query_lower or "6個月" in query_lower or "6 month" in query_lower:
                    time_period = "180d"
                    
            # 獲取技術指標
            result = get_technical_indicators(ticker, indicators, time_period)
            
            if "error" in result:
                return f"計算 {ticker} 技術指標時發生錯誤: {result['error']}"

            # 確保所有需要的鍵都存在
            if not all(k in result for k in ["company_name", "ticker", "current_price", "indicators"]):
                 return f"計算 {ticker} 技術指標時返回的數據格式不正確。"

            response = f"**{result['company_name']} ({result['ticker']})** 技術指標分析 📊\n\n"
            response += f"目前價格: ${result['current_price']:.2f}\n"
            response += f"分析週期: {time_period}\n\n"

            # 添加指標分析
            if "SMA" in result["indicators"]:
                sma = result["indicators"]["SMA"]
                # 確保 SMA 相關的鍵都存在
                if all(k in sma for k in ["SMA_20", "SMA_50", "Price_vs_SMA20", "Trend"]):
                    response += f"**SMA (簡單移動平均線)** 📉\n"
                    response += f"- SMA(20): ${sma['SMA_20']}\n"
                    response += f"- SMA(50): ${sma['SMA_50']}\n"
                    response += f"- 價格相對SMA(20): {sma['Price_vs_SMA20']}\n"
                    response += f"- 均線趨勢: {sma['Trend']}\n\n"

            if "RSI" in result["indicators"]:
                rsi = result["indicators"]["RSI"]
                 # 確保 RSI 相關的鍵都存在
                if all(k in rsi for k in ["RSI_14", "Signal"]):
                    response += f"**RSI (相對強弱指標)** 📊\n"
                    response += f"- RSI(14): {rsi['RSI_14']}\n"
                    response += f"- 信號: {rsi['Signal']}\n\n"

            if "MACD" in result["indicators"]:
                macd = result["indicators"]["MACD"]
                 # 確保 MACD 相關的鍵都存在
                if all(k in macd for k in ["MACD_line", "Signal_line", "Histogram", "Signal"]):
                    response += f"**MACD (移動平均收斂背離指標)** 📈\n"
                    response += f"- MACD線: {macd['MACD_line']}\n"
                    response += f"- 信號線: {macd['Signal_line']}\n"
                    response += f"- 柱狀圖: {macd['Histogram']}\n"
                    response += f"- 信號: {macd['Signal']}\n\n"

            response += "⚠️ 風險提醒: 技術分析僅供參考，投資決策應考慮多種因素。過往表現不代表未來結果。"

            return response
            
        elif "動能" in query_lower or "動量" in query_lower or "momentum" in query_lower:
            # 決定時間範圍
            time_period = "180d"  # 預設時間
            if "月" in query_lower or "month" in query_lower:
                if "一個月" in query_lower or "1個月" in query_lower or "1 month" in query_lower:
                    time_period = "30d"
                elif "三個月" in query_lower or "3個月" in query_lower or "3 month" in query_lower:
                    time_period = "90d"
                elif "六個月" in query_lower or "6個月" in query_lower or "6 month" in query_lower:
                    time_period = "180d"
                elif "一年" in query_lower or "1年" in query_lower or "1 year" in query_lower:
                    time_period = "365d"
                    
            # 獲取動能分析
            result = get_momentum_analysis(ticker, time_period)
            
            if "error" in result:
                return f"分析 {ticker} 動能時發生錯誤: {result['error']}"

            # 確保所有需要的鍵都存在
            if not all(k in result for k in ["name", "ticker", "momentum_score", "rating", "current_price", "analysis_period", "technical_summary", "recommendation"]):
                 return f"分析 {ticker} 動能時返回的數據格式不正確。"

            response = f"**{result['name']} ({result['ticker']})** 動能分析 🚀\n\n"
            response += f"動能評分: {result['momentum_score']}/100 ({result['rating']})\n"
            response += f"目前價格: ${result['current_price']:.2f}\n"
            response += f"分析週期: {result['analysis_period']}\n\n"

            response += "**技術指標摘要**:\n"
            if "technical_summary" in result:
                for name, value in result["technical_summary"].items():
                    response += f"- {name}: {value}\n"

            response += f"\n**建議**: {result['recommendation']}\n\n"

            response += "⚠️ 風險提醒: 動能分析僅供參考，投資決策應考慮多種因素。過往表現不代表未來結果。"

            return response
            
        elif "成交量" in query_lower or "volume" in query_lower:
            # 決定時間範圍
            time_period = "365d"  # 預設時間
            if "月" in query_lower or "month" in query_lower:
                if "一個月" in query_lower or "1個月" in query_lower or "1 month" in query_lower:
                    time_period = "30d"
                elif "三個月" in query_lower or "3個月" in query_lower or "3 month" in query_lower:
                    time_period = "90d"
                elif "六個月" in query_lower or "6個月" in query_lower or "6 month" in query_lower:
                    time_period = "180d"
                elif "一年" in query_lower or "1年" in query_lower or "1 year" in query_lower:
                    time_period = "365d"
                    
            # 獲取成交量分析
            result = get_volume_analysis(ticker, time_period)
            
            if "error" in result:
                return f"分析 {ticker} 成交量時發生錯誤: {result['error']}"

            # 確保所有需要的鍵都存在
            if not all(k in result for k in ["name", "ticker", "current_price", "analysis_period", "volume_indicators", "volume_trend", "vwap_analysis", "analysis"]):
                 return f"分析 {ticker} 成交量時返回的數據格式不正確。"

            response = f"**{result['name']} ({result['ticker']})** 成交量分析 📊\n\n"
            response += f"目前價格: ${result['current_price']:.2f}\n"
            response += f"分析週期: {result['analysis_period']}\n\n"

            response += "**成交量指標**:\n"
            if "volume_indicators" in result:
                for name, value in result["volume_indicators"].items():
                    response += f"- {name}: {value}\n"

            response += f"\n**成交量趨勢**: {result['volume_trend']}\n"
            response += f"**VWAP分析**: {result['vwap_analysis']}\n"
            response += f"**綜合分析**: {result['analysis']}\n\n"

            response += "⚠️ 風險提醒: 成交量分析僅供參考，投資決策應考慮多種因素。過往表現不代表未來結果。"

            return response
            
        else:
            # 默認進行綜合分析 (動能分析)
            result = get_momentum_analysis(ticker)
            
            if "error" in result:
                return f"分析 {ticker} 時發生錯誤: {result['error']}"

            # 確保所有需要的鍵都存在
            if not all(k in result for k in ["name", "ticker", "momentum_score", "rating", "current_price", "technical_summary", "recommendation"]):
                 return f"分析 {ticker} 時返回的數據格式不正確。"

            response = f"**{result['name']} ({result['ticker']})** 綜合分析 📊\n\n"
            response += f"動能評分: {result['momentum_score']}/100 ({result['rating']})\n"
            response += f"目前價格: ${result['current_price']:.2f}\n\n"

            response += "**技術指標摘要**:\n"
            if "technical_summary" in result:
                for name, value in result["technical_summary"].items():
                    response += f"- {name}: {value}\n"

            response += f"\n**建議**: {result['recommendation']}\n\n"

            response += "⚠️ 風險提醒: 投資有風險，入市需謹慎。過往表現不代表未來結果。"

            return response
            
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

# 顯示資訊
st.sidebar.info("⚠️ 使用簡化版股票分析工具 (無 LLM)")
