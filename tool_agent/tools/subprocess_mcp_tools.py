"""
通過 subprocess 調用 MCP 工具 - 最穩定嘅方法
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
    通過 subprocess 調用 MCP 函數
    """
    try:
        # 創建 Python 腳本
        script = f"""
import sys
sys.path.insert(0, '{MCP_SCRIPT_DIR}')
import os
os.environ['TIINGO_API_KEY'] = '{os.environ.get("TIINGO_API_KEY", "2146105fde5488455a958c98755941aafb9d9c66")}'
import stock_ta_tool
import json

try:
    if '{function_name}' == 'get_stock_price':
        # 模擬 get_stock_price 功能
        df = stock_ta_tool.get_stock_data('{kwargs.get("ticker", "AAPL")}', '30d')
        if not df.empty:
            latest = df.iloc[-1]
            result = {{
                'ticker': '{kwargs.get("ticker", "AAPL")}',
                'current_price': float(latest['close']),
                'open_price': float(latest['open']),
                'high_price': float(latest['high']),
                'low_price': float(latest['low']),
                'volume': int(latest['volume']),
                'date': latest.name.strftime('%Y-%m-%d'),
                'company_name': stock_ta_tool.get_stock_name('{kwargs.get("ticker", "AAPL")}'),
                'status': 'success'
            }}
        else:
            result = {{'error': '無法獲取股票數據', 'ticker': '{kwargs.get("ticker", "AAPL")}'}}
    
    elif '{function_name}' == 'get_technical_indicators':
        indicators = {repr(kwargs.get("indicators", ["SMA", "EMA", "RSI", "MACD"]))}
        result = stock_ta_tool.get_technical_indicators(
            ticker='{kwargs.get("ticker", "AAPL")}',
            indicators=indicators,
            time_period='{kwargs.get("time_period", "365d")}'
        )
    
    elif '{function_name}' == 'get_momentum_analysis':
        result = stock_ta_tool.momentum_stock_score(
            ticker='{kwargs.get("ticker", "AAPL")}',
            time_period='{kwargs.get("time_period", "180d")}'
        )
    
    else:
        result = {{'error': f'未知函數: {function_name}'}}
    
    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({{'error': f'執行失敗: {{str(e)}}', 'function': '{function_name}'}}, ensure_ascii=False))
"""
        
        # 執行腳本
        process = subprocess.run(
            [MCP_PYTHON, '-c', script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if process.returncode == 0:
            try:
                result = json.loads(process.stdout.strip())
                return result
            except json.JSONDecodeError:
                return {
                    "error": f"無法解析 JSON 輸出",
                    "stdout": process.stdout,
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
    獲取股票當前價格（subprocess 版本）
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
    計算股票技術指標（subprocess 版本）
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
    進行股票動量分析（subprocess 版本）
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
