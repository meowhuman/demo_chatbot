"""
直接 MCP 工具整合 - 含診斷功能
"""
import sys
import os
from typing import Dict, Any
from .mcp_diagnosis import diagnose_mcp_import, get_stock_price_fallback, get_technical_indicators_fallback, get_momentum_analysis_fallback

# 添加 MCP 伺服器路徑到 Python path
MCP_SERVER_PATH = '/Volumes/Ketomuffin_mac/AI/mcpserver/mcp-stock-ta'
if MCP_SERVER_PATH not in sys.path:
    sys.path.insert(0, MCP_SERVER_PATH)

# 設置環境變數
os.environ['TIINGO_API_KEY'] = os.environ.get('TIINGO_API_KEY', '2146105fde5488455a958c98755941aafb9d9c66')

# 進行診斷並嘗試導入
print("🔍 正在診斷 MCP 模組...")
diagnosis = diagnose_mcp_import()

# 嘗試直接 import MCP 工具模組
try:
    import stock_ta_tool
    print("✅ 成功導入 stock_ta_tool 模組")
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"❌ 無法導入 stock_ta_tool: {e}")
    print("📋 診斷結果:")
    for key, value in diagnosis.items():
        if key != "recommendations":
            print(f"  {key}: {value}")
    print("💡 建議:")
    for rec in diagnosis["recommendations"]:
        print(f"  - {rec}")
    MCP_AVAILABLE = False

def get_stock_price(ticker: str) -> Dict[str, Any]:
    """
    獲取股票當前價格和基本信息（帶診斷版本）
    """
    if not MCP_AVAILABLE:
        return get_stock_price_fallback(ticker)
    
    try:
        print(f"🔄 正在獲取 {ticker} 股價...")
        
        # 直接調用 MCP 工具函數
        # 使用正確的函數名稱（從 server.py 可以看到是 get_stock_price）
        df = stock_ta_tool.get_stock_data(ticker, time_period="30d")  # 使用較短時間範圍
        
        if df.empty:
            return {
                "error": f"無法獲取 {ticker} 的股票數據",
                "ticker": ticker
            }
        
        # 獲取最新數據
        latest_data = df.iloc[-1]
        company_name = stock_ta_tool.get_stock_name(ticker)
        
        # 構建價格信息
        result = {
            "ticker": ticker.upper(),
            "company_name": company_name,
            "current_price": round(float(latest_data['close']), 2),
            "open_price": round(float(latest_data['open']), 2),
            "high_price": round(float(latest_data['high']), 2),
            "low_price": round(float(latest_data['low']), 2),
            "volume": int(latest_data['volume']),
            "date": latest_data.name.strftime('%Y-%m-%d'),
            "status": "success"
        }
        
        # 計算變動（如果有足夠數據）
        if len(df) > 1:
            prev_data = df.iloc[-2]
            change = latest_data['close'] - prev_data['close']
            change_percent = (change / prev_data['close']) * 100
            
            result["day_change"] = round(float(change), 2)
            result["day_change_percent"] = round(float(change_percent), 2)
        
        print(f"✅ 成功獲取 {ticker} 股價")
        return result
        
    except Exception as e:
        print(f"❌ 獲取股價失敗: {e}")
        return {
            "error": f"獲取股價失敗: {str(e)}",
            "ticker": ticker
        }

def get_technical_indicators(ticker: str, indicators: str = "SMA,EMA,RSI,MACD", time_period: str = "365d") -> Dict[str, Any]:
    """
    計算股票技術指標（帶診斷版本）
    """
    if not MCP_AVAILABLE:
        return get_technical_indicators_fallback(ticker, indicators, time_period)
    
    try:
        print(f"🔄 正在計算 {ticker} 技術指標: {indicators}")
        
        # 轉換指標字符串為列表
        indicator_list = [ind.strip().upper() for ind in indicators.split(',')]
        
        # 直接調用 MCP 工具函數
        result = stock_ta_tool.get_technical_indicators(
            ticker=ticker,
            indicators=indicator_list,
            time_period=time_period
        )
        
        if "error" not in result:
            print(f"✅ 成功計算 {ticker} 技術指標")
        
        return result
        
    except Exception as e:
        print(f"❌ 技術指標計算失敗: {e}")
        return {
            "error": f"技術指標計算失敗: {str(e)}",
            "ticker": ticker,
            "indicators": indicators
        }

def get_momentum_analysis(ticker: str, time_period: str = "180d") -> Dict[str, Any]:
    """
    進行股票動量分析（帶診斷版本）
    """
    if not MCP_AVAILABLE:
        return get_momentum_analysis_fallback(ticker, time_period)
    
    try:
        print(f"🔄 正在進行 {ticker} 動量分析...")
        
        # 直接調用 MCP 工具函數
        result = stock_ta_tool.momentum_stock_score(
            ticker=ticker,
            time_period=time_period
        )
        
        if "error" not in result:
            print(f"✅ 成功完成 {ticker} 動量分析")
        
        return result
        
    except Exception as e:
        print(f"❌ 動量分析失敗: {e}")
        return {
            "error": f"動量分析失敗: {str(e)}",
            "ticker": ticker,
            "time_period": time_period
        }

def list_available_indicators() -> Dict[str, Any]:
    """
    列出所有可用的技術指標
    """
    return {
        "basic_indicators": {
            "SMA": "簡單移動平均線 - 計算指定期間的平均價格",
            "EMA": "指數移動平均線 - 對近期價格給予更多權重",
            "RSI": "相對強弱指標 - 衡量價格變動的速度和幅度 (0-100)",
            "MACD": "移動平均收斂背離指標 - 顯示兩條移動平均線的關係",
            "BOLLINGER": "布林通道 - 基於移動平均線和標準差的價格通道",
            "STOCHASTIC": "隨機指標 - 比較收盤價與價格範圍的關係",
            "WILLIAMS_R": "威廉指標 - 衡量超買超賣的動量振盪器",
            "ADX": "平均趨向指標 - 衡量趨勢強度 (不包括方向)",
            "ATR": "平均真實範圍 - 衡量價格波動性",
            "CCI": "商品通道指標 - 識別周期性趨勢的動量指標"
        },
        "usage_examples": {
            "basic_analysis": "get_technical_indicators('AAPL', 'SMA,EMA,RSI,MACD')",
            "momentum_analysis": "get_momentum_analysis('AAPL', '180d')",
            "get_price": "get_stock_price('AAPL')"
        },
        "mcp_status": "可用" if MCP_AVAILABLE else "不可用",
        "data_source": "Tiingo API" if MCP_AVAILABLE else "無"
    }

def check_mcp_status() -> Dict[str, Any]:
    """
    檢查 MCP 模組狀態（詳細診斷版本）
    """
    return {
        "mcp_available": MCP_AVAILABLE,
        "detailed_diagnosis": diagnosis,
        "quick_status": {
            "path_exists": diagnosis["path_status"]["mcp_directory_exists"],
            "file_exists": diagnosis["path_status"]["stock_ta_tool_exists"],
            "dependencies_ok": all("已安裝" in status for status in diagnosis["dependency_status"].values()),
            "import_successful": "成功導入" in diagnosis["import_status"].get("stock_ta_tool", "")
        },
        "recommendations": diagnosis["recommendations"]
    }
