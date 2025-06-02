"""
MCP 模組導入診斷工具
"""
import sys
import os
from typing import Dict, Any

def diagnose_mcp_import() -> Dict[str, Any]:
    """診斷 MCP 模組導入問題"""
    
    diagnosis = {
        "mcp_server_path": "/Volumes/Ketomuffin_mac/AI/mcpserver/mcp-stock-ta",
        "import_status": {},
        "path_status": {},
        "dependency_status": {},
        "recommendations": []
    }
    
    # 檢查路徑
    mcp_path = diagnosis["mcp_server_path"]
    diagnosis["path_status"]["mcp_directory_exists"] = os.path.exists(mcp_path)
    diagnosis["path_status"]["stock_ta_tool_exists"] = os.path.exists(os.path.join(mcp_path, "stock_ta_tool.py"))
    diagnosis["path_status"]["python_path_added"] = mcp_path in sys.path
    
    # 嘗試添加路徑
    if mcp_path not in sys.path:
        sys.path.insert(0, mcp_path)
        diagnosis["path_status"]["python_path_added"] = True
    
    # 嘗試導入依賴
    dependencies = ["pandas", "numpy", "requests", "talib"]
    
    for dep in dependencies:
        try:
            if dep == "talib":
                import talib
                diagnosis["dependency_status"][dep] = "已安裝"
            elif dep == "pandas":
                import pandas
                diagnosis["dependency_status"][dep] = "已安裝"
            elif dep == "numpy":
                import numpy
                diagnosis["dependency_status"][dep] = "已安裝"
            elif dep == "requests":
                import requests
                diagnosis["dependency_status"][dep] = "已安裝"
        except ImportError as e:
            diagnosis["dependency_status"][dep] = f"未安裝: {str(e)}"
    
    # 嘗試導入 MCP 模組
    try:
        import stock_ta_tool
        diagnosis["import_status"]["stock_ta_tool"] = "成功導入"
        
        # 檢查可用函數
        functions = [func for func in dir(stock_ta_tool) if callable(getattr(stock_ta_tool, func)) and not func.startswith('_')]
        diagnosis["import_status"]["available_functions"] = functions
        
    except ImportError as e:
        diagnosis["import_status"]["stock_ta_tool"] = f"導入失敗: {str(e)}"
    except Exception as e:
        diagnosis["import_status"]["stock_ta_tool"] = f"未知錯誤: {str(e)}"
    
    # 生成建議
    if not diagnosis["path_status"]["mcp_directory_exists"]:
        diagnosis["recommendations"].append("MCP 伺服器目錄不存在，請檢查路徑")
    
    if not diagnosis["path_status"]["stock_ta_tool_exists"]:
        diagnosis["recommendations"].append("stock_ta_tool.py 檔案不存在")
    
    for dep, status in diagnosis["dependency_status"].items():
        if "未安裝" in status:
            if dep == "talib":
                diagnosis["recommendations"].append(f"需要安裝 {dep}: 在 MCP 環境中執行 'pip install TA-Lib'")
            else:
                diagnosis["recommendations"].append(f"需要安裝 {dep}: pip install {dep}")
    
    if "成功導入" not in diagnosis["import_status"].get("stock_ta_tool", ""):
        diagnosis["recommendations"].append("stock_ta_tool 模組導入失敗，請檢查依賴和路徑")
    
    return diagnosis

def get_stock_price_fallback(ticker: str) -> Dict[str, Any]:
    """
    後備股票價格查詢（如果 MCP 不可用）
    """
    return {
        "ticker": ticker.upper(),
        "error": "MCP 模組不可用",
        "fallback_note": "請檢查 MCP 伺服器和依賴",
        "suggested_actions": [
            "檢查 MCP 伺服器路徑",
            "確認依賴已安裝（特別是 TA-Lib）",
            "檢查 TIINGO_API_KEY 環境變數"
        ]
    }

def get_technical_indicators_fallback(ticker: str, indicators: str = "SMA,EMA,RSI,MACD", time_period: str = "365d") -> Dict[str, Any]:
    """
    後備技術指標查詢（如果 MCP 不可用）
    """
    return {
        "ticker": ticker.upper(),
        "indicators": indicators,
        "time_period": time_period,
        "error": "MCP 模組不可用",
        "fallback_note": "無法計算技術指標",
        "suggested_actions": [
            "檢查 MCP 伺服器路徑",
            "確認依賴已安裝（特別是 TA-Lib）",
            "檢查 TIINGO_API_KEY 環境變數"
        ]
    }

def get_momentum_analysis_fallback(ticker: str, time_period: str = "180d") -> Dict[str, Any]:
    """
    後備動量分析（如果 MCP 不可用）
    """
    return {
        "ticker": ticker.upper(),
        "time_period": time_period,
        "error": "MCP 模組不可用",
        "fallback_note": "無法進行動量分析",
        "suggested_actions": [
            "檢查 MCP 伺服器路徑",
            "確認依賴已安裝（特別是 TA-Lib）",
            "檢查 TIINGO_API_KEY 環境變數"
        ]
    }
