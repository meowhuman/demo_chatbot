"""
通過 subprocess 調用 MCP 工具 - 清潔版本（無調試輸出）
"""
import subprocess
import json
import os
from typing import Dict, Any

# MCP 環境路徑
MCP_PYTHON = '/Volumes/Ketomuffin_mac/AI/mcpserver/mcp-stock-ta/.venv/bin/python'
MCP_SCRIPT_DIR = '/Volumes/Ketomuffin_mac/AI/mcpserver/mcp-stock-ta'

def _run_mcp_function(function_name: str, **kwargs) -> Dict[str, Any]:
    """
    通過 subprocess 調用 MCP 函數（清潔版本）
    """
    try:
        # 創建清潔嘅 Python 腳本（無調試輸出）
        if function_name == 'get_stock_price':
            script = f'''
import sys
import os
import json
sys.path.insert(0, "{MCP_SCRIPT_DIR}")
os.environ["TIINGO_API_KEY"] = "{os.environ.get("TIINGO_API_KEY", "2146105fde5488455a958c98755941aafb9d9c66")}"

# 抑制所有輸出除咗最終 JSON
import io
class SuppressOutput:
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self
    def __exit__(self, *args):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

try:
    with SuppressOutput():
        import stock_ta_tool
        df = stock_ta_tool.get_stock_data("{kwargs.get("ticker", "AAPL")}", "30d")
        company_name = stock_ta_tool.get_stock_name("{kwargs.get("ticker", "AAPL")}")
    
    if not df.empty:
        latest = df.iloc[-1]
        result = {{
            "ticker": "{kwargs.get("ticker", "AAPL")}",
            "current_price": float(latest["close"]),
            "open_price": float(latest["open"]),
            "high_price": float(latest["high"]),
            "low_price": float(latest["low"]),
            "volume": int(latest["volume"]),
            "date": latest.name.strftime("%Y-%m-%d"),
            "company_name": company_name,
            "status": "success"
        }}
    else:
        result = {{"error": "無法獲取股票數據", "ticker": "{kwargs.get("ticker", "AAPL")}"}}
    
    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({{"error": f"執行失敗: {{str(e)}}", "function": "{function_name}"}}, ensure_ascii=False))
'''
        
        elif function_name == 'get_technical_indicators':
            indicators_list = kwargs.get("indicators", ["SMA", "EMA", "RSI", "MACD"])
            script = f'''
import sys
import os
import json
sys.path.insert(0, "{MCP_SCRIPT_DIR}")
os.environ["TIINGO_API_KEY"] = "{os.environ.get("TIINGO_API_KEY", "2146105fde5488455a958c98755941aafb9d9c66")}"

import io
class SuppressOutput:
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self
    def __exit__(self, *args):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

try:
    with SuppressOutput():
        import stock_ta_tool
        result = stock_ta_tool.get_technical_indicators(
            ticker="{kwargs.get("ticker", "AAPL")}",
            indicators={indicators_list},
            time_period="{kwargs.get("time_period", "365d")}"
        )
    
    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({{"error": f"執行失敗: {{str(e)}}", "function": "{function_name}"}}, ensure_ascii=False))
'''

        elif function_name == 'get_volume_analysis':
            script = f'''
import sys
import os
import json
sys.path.insert(0, "{MCP_SCRIPT_DIR}")
os.environ["TIINGO_API_KEY"] = "{os.environ.get("TIINGO_API_KEY", "2146105fde5488455a958c98755941aafb9d9c66")}"

import io
class SuppressOutput:
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self
    def __exit__(self, *args):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

try:
    with SuppressOutput():
        import stock_ta_tool
        from volume_indicators import get_volume_indicators_analysis, get_volume_indicator_description
        
        # 獲取股票數據
        df = stock_ta_tool.get_stock_data("{kwargs.get("ticker", "AAPL")}", "{kwargs.get("time_period", "365d")}")
        
        if df.empty:
            result = {{"error": "無法獲取股票數據", "ticker": "{kwargs.get("ticker", "AAPL")}"}}
        else:
            # 計算成交量指標
            volume_analysis = get_volume_indicators_analysis(df, None)
            
            # 準備結果
            results = {{
                "ticker": "{kwargs.get("ticker", "AAPL")}",
                "company_name": stock_ta_tool.get_stock_name("{kwargs.get("ticker", "AAPL")}"),
                "current_price": float(df["close"].iloc[-1]),
                "data_points": len(df),
                "time_period": "{kwargs.get("time_period", "365d")}",
                "volume_indicators": {{}},
                "available_indicators": [
                    "VWAP", "OBV", "MFI", "Volume_Oscillator", 
                    "AD_Line", "Chaikin_Oscillator", "Force_Index", "VWMA"
                ]
            }}
            
            # 提取當前指標值
            current_price = float(df["close"].iloc[-1])
            
            for indicator_name, indicator_series in volume_analysis.items():
                if indicator_name in ["analysis", "error"]:
                    continue
                    
                if hasattr(indicator_series, "iloc") and len(indicator_series) > 0:
                    try:
                        current_value = float(indicator_series.iloc[-1]) if not stock_ta_tool.pd.isna(indicator_series.iloc[-1]) else None
                        previous_value = float(indicator_series.iloc[-2]) if len(indicator_series) > 1 and not stock_ta_tool.pd.isna(indicator_series.iloc[-2]) else None
                        
                        indicator_result = {{
                            "current_value": round(current_value, 4) if current_value is not None else None,
                            "previous_value": round(previous_value, 4) if previous_value is not None else None,
                            "description": get_volume_indicator_description(indicator_name)
                        }}
                        
                        # 添加特定指標的解釋
                        if indicator_name == "VWAP" and current_value:
                            deviation = ((current_price - current_value) / current_value) * 100
                            indicator_result["price_vs_vwap"] = round(deviation, 2)
                            indicator_result["signal"] = "BULLISH" if deviation > 1 else "BEARISH" if deviation < -1 else "NEUTRAL"
                        
                        elif indicator_name == "MFI" and current_value:
                            indicator_result["signal"] = "OVERBOUGHT" if current_value > 80 else "OVERSOLD" if current_value < 20 else "NEUTRAL"
                        
                        elif indicator_name == "OBV" and current_value and previous_value:
                            indicator_result["trend"] = "UP" if current_value > previous_value else "DOWN"
                        
                        results["volume_indicators"][indicator_name] = indicator_result
                    except Exception:
                        continue
            
            result = results
    
    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({{"error": f"執行失敗: {{str(e)}}", "function": "{function_name}"}}, ensure_ascii=False))
'''

        elif function_name == 'get_momentum_analysis':
            script = f'''
import sys
import os
import json
sys.path.insert(0, "{MCP_SCRIPT_DIR}")
os.environ["TIINGO_API_KEY"] = "{os.environ.get("TIINGO_API_KEY", "2146105fde5488455a958c98755941aafb9d9c66")}"

import io
class SuppressOutput:
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self
    def __exit__(self, *args):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

try:
    with SuppressOutput():
        import stock_ta_tool
        result = stock_ta_tool.momentum_stock_score(
            ticker="{kwargs.get("ticker", "AAPL")}",
            time_period="{kwargs.get("time_period", "180d")}"
        )
    
    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({{"error": f"執行失敗: {{str(e)}}", "function": "{function_name}"}}, ensure_ascii=False))
'''
        else:
            return {"error": f"未知函數: {function_name}"}
        
        # 執行腳本
        process = subprocess.run(
            [MCP_PYTHON, '-c', script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if process.returncode == 0:
            try:
                # 只解析最後一行（JSON 結果）
                output_lines = process.stdout.strip().split('\\n')
                json_line = output_lines[-1] if output_lines else ""
                
                if json_line:
                    result = json.loads(json_line)
                    return result
                else:
                    return {
                        "error": "無輸出",
                        "stderr": process.stderr
                    }
            except json.JSONDecodeError as e:
                return {
                    "error": f"JSON 解析失敗: {str(e)}",
                    "raw_output": process.stdout,
                    "stderr": process.stderr
                }
        else:
            return {
                "error": f"subprocess 執行失敗 (exit code: {process.returncode})",
                "stderr": process.stderr,
                "stdout": process.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {
            "error": "執行超時",
            "function": function_name
        }
    except Exception as e:
        return {
            "error": f"subprocess 調用失敗: {str(e)}",
            "function": function_name
        }

def get_stock_price(ticker: str) -> Dict[str, Any]:
    """
    獲取股票當前價格（清潔版本）
    """
    print(f"🔄 正在通過 subprocess 獲取 {ticker} 股價...")
    
    result = _run_mcp_function("get_stock_price", ticker=ticker)
    
    if "error" not in result:
        print(f"✅ 成功獲取 {ticker} 股價")
    else:
        print(f"❌ 獲取股價失敗: {result.get('error')}")
    
    return result

def get_technical_indicators(ticker: str, indicators: str = "SMA,EMA,RSI,MACD", time_period: str = "365d") -> Dict[str, Any]:
    """
    計算股票技術指標（清潔版本）
    """
    print(f"🔄 正在通過 subprocess 計算 {ticker} 技術指標: {indicators}")
    
    # 轉換指標字符串為列表
    indicator_list = [ind.strip().upper() for ind in indicators.split(',')]
    
    result = _run_mcp_function("get_technical_indicators", 
                              ticker=ticker, 
                              indicators=indicator_list, 
                              time_period=time_period)
    
    if "error" not in result:
        print(f"✅ 成功計算 {ticker} 技術指標")
    else:
        print(f"❌ 技術指標計算失敗: {result.get('error')}")
    
    return result

def get_momentum_analysis(ticker: str, time_period: str = "180d") -> Dict[str, Any]:
    """
    進行股票動量分析（清潔版本）
    """
    print(f"🔄 正在通過 subprocess 進行 {ticker} 動量分析...")
    
    result = _run_mcp_function("get_momentum_analysis", 
                              ticker=ticker, 
                              time_period=time_period)
    
    if "error" not in result:
        print(f"✅ 成功完成 {ticker} 動量分析")
    else:
        print(f"❌ 動量分析失敗: {result.get('error')}")
    
    return result

def get_volume_analysis(ticker: str, time_period: str = "365d") -> Dict[str, Any]:
    """
    進行成交量技術分析（清潔版本）
    """
    print(f"🔄 正在通過 subprocess 進行 {ticker} 成交量分析...")
    
    result = _run_mcp_function("get_volume_analysis", 
                              ticker=ticker, 
                              time_period=time_period)
    
    if "error" not in result:
        print(f"✅ 成功完成 {ticker} 成交量分析")
    else:
        print(f"❌ 成交量分析失敗: {result.get('error')}")
    
    return result

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
            "ADX": "平均趨向指標 - 衡量趨勢強度",
            "ATR": "平均真實範圍 - 衡量價格波動性",
            "CCI": "商品通道指標 - 識別周期性趨勢的動量指標"
        },
        "volume_indicators": {
            "VWAP": "成交量加權平均價格 - 重要的交易基準價格",
            "OBV": "平衡成交量 - 結合價格和成交量的動量指標",
            "MFI": "資金流量指標 - 基於成交量的 RSI，衡量買賣壓力",
            "Volume_Oscillator": "成交量震盪指標 - 衡量短期與長期成交量關係",
            "AD_Line": "累積分佈線 - 判斷資金流入或流出",
            "Chaikin_Oscillator": "蔡金震盪指標 - A/D線的動量版本",
            "Force_Index": "力量指標 - 結合價格變化和成交量的力量衡量",
            "VWMA": "成交量加權移動平均線 - 基於成交量權重的移動平均"
        },
        "usage_examples": {
            "basic_analysis": "get_technical_indicators('AAPL', 'SMA,EMA,RSI,MACD')",
            "momentum_analysis": "get_momentum_analysis('AAPL', '180d')",
            "volume_analysis": "get_volume_analysis('AAPL', '365d')",  # 新增
            "get_price": "get_stock_price('AAPL')"
        },
        "data_source": "Tiingo API（通過 subprocess 調用）",
        "method": "subprocess",
        "status": "可用"
    }

def check_mcp_status() -> Dict[str, Any]:
    """
    檢查 MCP subprocess 狀態
    """
    try:
        # 測試基本調用
        test_result = _run_mcp_function("get_stock_price", ticker="AAPL")
        
        return {
            "method": "subprocess",
            "mcp_python_path": MCP_PYTHON,
            "mcp_script_dir": MCP_SCRIPT_DIR,
            "python_exists": os.path.exists(MCP_PYTHON),
            "script_dir_exists": os.path.exists(MCP_SCRIPT_DIR),
            "test_call_result": "成功" if "error" not in test_result else f"失敗: {test_result.get('error')}",
            "status": "正常" if "error" not in test_result else "有問題",
            "tiingo_api_key": "已設置" if os.environ.get('TIINGO_API_KEY') else "未設置"
        }
        
    except Exception as e:
        return {
            "method": "subprocess",
            "status": "失敗",
            "error": str(e)
        }
