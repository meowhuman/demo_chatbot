"""
真實版 MCP 股票分析工具 - 修復版本
使用真實工具模組成功結果，並聯接真實版 MCP 服務器
"""
import asyncio
import os
import threading
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
import subprocess
import json
import time

# MCP 聯接設定
MCP_SERVER_PATH = '/Volumes/Ketomuffin_mac/AI/mcpserver/mcp-stock-ta'
PYTHON_INTERPRETER = os.path.join(MCP_SERVER_PATH, '.venv/bin/python')
SERVER_SCRIPT = os.path.join(MCP_SERVER_PATH, 'server.py')

# 全局變數
_mcp_process = None
_process_lock = threading.Lock()

def _start_mcp_server():
    """啟動 MCP 服務器進程"""
    global _mcp_process
    
    with _process_lock:
        if _mcp_process is None or _mcp_process.poll() is not None:
            try:
                # 設置環境變數
                env = os.environ.copy()
                env['TIINGO_API_KEY'] = os.environ.get('TIINGO_API_KEY', '')
                
                # 啟動 MCP 服務器
                _mcp_process = subprocess.Popen(
                    [PYTHON_INTERPRETER, SERVER_SCRIPT],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True,
                    bufsize=0
                )
                
                print(f"✅ MCP 服務器已啟動，PID: {_mcp_process.pid}")
                time.sleep(2)  # 等待服務器啟動
                
                return True
                
            except Exception as e:
                print(f"❌ 啟動 MCP 服務器失敗: {e}")
                return False
    
    return True

def _call_mcp_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """直接使用 MCP 工具"""
    try:
        # 確保 MCP 服務器運行
        if not _start_mcp_server():
            return {"error": "無法啟動 MCP 服務器"}
        
        # 構建 MCP 請求
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        # 發送請求到 MCP 服務器
        request_json = json.dumps(request) + '\n'
        
        with _process_lock:
            if _mcp_process and _mcp_process.poll() is None:
                _mcp_process.stdin.write(request_json)
                _mcp_process.stdin.flush()
                
                # 獲取響應
                response_line = _mcp_process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    
                    if 'result' in response:
                        return response['result']
                    elif 'error' in response:
                        return {"error": f"MCP 錯誤: {response['error']}"}
                    else:
                        return {"error": "未知 MCP 響應格式"}
                else:
                    return {"error": "MCP 服務器無響應"}
            else:
                return {"error": "MCP 服務器進程不可用"}
        
    except Exception as e:
        return {"error": f"MCP 使用失敗: {str(e)}"}

def get_stock_price(ticker: str) -> Dict[str, Any]:
    """
    獲取股票當前價格和基本信息（真正 MCP 版本）
    
    Args:
        ticker: 股票代碼 (例如 "AAPL", "TSLA", "GOOGL")
    
    Returns:
        包含股票價格信息的字典
    """
    try:
        print(f"🔄 正在通過 MCP 獲取 {ticker} 股價...")
        
        result = _call_mcp_tool("get_stock_price", {"ticker": ticker})
        
        if "error" not in result:
            print(f"✅ 成功獲取 {ticker} 股價")
        
        return result
        
    except Exception as e:
        print(f"❌ 獲取股價失敗: {e}")
        return {
            "error": f"獲取股價失敗: {str(e)}",
            "ticker": ticker,
            "fallback_note": "請檢查 MCP 服務器聯接"
        }

def get_technical_indicators(ticker: str, indicators: str = "SMA,EMA,RSI,MACD", time_period: str = "365d") -> Dict[str, Any]:
    """
    計算股票技術指標（真正 MCP 版本）
    
    Args:
        ticker: 股票代碼 (例如 "AAPL", "TSLA")
        indicators: 技術指標，逗號分隔 (例如 "SMA,EMA,RSI,MACD")
        time_period: 時間範圍 (例如 "90d", "180d", "1y")
    
    Returns:
        包含技術指標分析結果的字典
    """
    try:
        print(f"🔄 正在通過 MCP 計算 {ticker} 技術指標: {indicators}")
        
        # 轉換指標字符串為列表
        indicator_list = [ind.strip().upper() for ind in indicators.split(',')]
        
        result = _call_mcp_tool("get_technical_indicators", {
            "ticker": ticker,
            "indicators": indicator_list,
            "time_period": time_period
        })
        
        if "error" not in result:
            print(f"✅ 成功計算 {ticker} 技術指標")
        
        return result
        
    except Exception as e:
        print(f"❌ 技術指標計算失敗: {e}")
        return {
            "error": f"技術指標計算失敗: {str(e)}",
            "ticker": ticker,
            "indicators": indicators,
            "fallback_note": "請檢查 MCP 服務器聯接"
        }

def get_momentum_analysis(ticker: str, time_period: str = "180d") -> Dict[str, Any]:
    """
    執行股票動量分析（真正 MCP 版本）
    
    Args:
        ticker: 股票代碼 (例如 "AAPL", "TSLA")
        time_period: 分析時間範圍 (例如 "90d", "180d", "1y")
    
    Returns:
        包含動量分析結果的字典
    """
    try:
        print(f"🔄 正在通過 MCP 執行 {ticker} 動量分析...")
        
        result = _call_mcp_tool("get_momentum_stock_analysis", {
            "ticker": ticker,
            "time_period": time_period
        })
        
        if "error" not in result:
            print(f"✅ 成功完成 {ticker} 動量分析")
        
        return result
        
    except Exception as e:
        print(f"❌ 動量分析失敗: {e}")
        return {
            "error": f"動量分析失敗: {str(e)}",
            "ticker": ticker,
            "time_period": time_period,
            "fallback_note": "請檢查 MCP 服務器聯接"
        }

def get_volume_analysis(ticker: str, time_period: str = "365d") -> Dict[str, Any]:
    """
    執行成交量技術分析（真正 MCP 版本）
    
    Args:
        ticker: 股票代碼 (例如 "AAPL", "TSLA") 
        time_period: 分析時間範圍 (例如 "90d", "180d", "1y")
    
    Returns:
        包含成交量分析結果的字典
    """
    try:
        print(f"🔄 正在通過 MCP 執行 {ticker} 成交量分析...")
        
        result = _call_mcp_tool("get_volume_technical_analysis", {
            "ticker": ticker,
            "time_period": time_period
        })
        
        if "error" not in result:
            print(f"✅ 成功完成 {ticker} 成交量分析")
        
        return result
        
    except Exception as e:
        print(f"❌ 成交量分析失敗: {e}")
        return {
            "error": f"成交量分析失敗: {str(e)}",
            "ticker": ticker,
            "time_period": time_period,
            "fallback_note": "請檢查 MCP 服務器聯接"
        }

def list_available_indicators() -> Dict[str, Any]:
    """
    列出所有可用的技術指標（真正 MCP 版本）
    
    Returns:
        包含可用指標說明的字典
    """
    try:
        print(f"🔄 正在通過 MCP 獲取可用指標列表...")
        
        result = _call_mcp_tool("list_available_indicators", {})
        
        if "error" not in result:
            print(f"✅ 成功獲取指標列表")
        
        return result
        
    except Exception as e:
        print(f"❌ 獲取指標列表失敗: {e}")
        return {
            "error": f"獲取指標列表失敗: {str(e)}",
            "fallback_note": "請檢查 MCP 服務器聯接"
        }

def check_mcp_status() -> Dict[str, Any]:
    """
    檢查 MCP 服務器狀態
    
    Returns:
        包含 MCP 服務器狀態信息的字典
    """
    global _mcp_process
    
    status = {
        "mcp_server_path": MCP_SERVER_PATH,
        "python_interpreter": PYTHON_INTERPRETER,
        "server_script": SERVER_SCRIPT,
    }
    
    # 檢查路徑
    if os.path.exists(PYTHON_INTERPRETER):
        status["python_interpreter_exists"] = True
    else:
        status["python_interpreter_exists"] = False
        status["error"] = f"Python 解釋器不存在: {PYTHON_INTERPRETER}"
    
    if os.path.exists(SERVER_SCRIPT):
        status["server_script_exists"] = True
    else:
        status["server_script_exists"] = False
        status["error"] = f"服務器腳本不存在: {SERVER_SCRIPT}"
    
    # 檢查進程狀態
    if _mcp_process:
        if _mcp_process.poll() is None:
            status["process_status"] = "running"
            status["process_pid"] = _mcp_process.pid
        else:
            status["process_status"] = "stopped"
            status["process_exit_code"] = _mcp_process.poll()
    else:
        status["process_status"] = "not_started"
    
    # 檢查環境變數
    tiingo_key = os.environ.get('TIINGO_API_KEY')
    if tiingo_key:
        status["tiingo_api_key"] = f"已設置 (長度: {len(tiingo_key)})"
    else:
        status["tiingo_api_key"] = "未設置"
        status["warning"] = "TIINGO_API_KEY 環境變數未設置"
    
    return status
