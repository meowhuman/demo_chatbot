"""
MCP Stock Analysis Tools - ADK Compatible
呢個模組提供標準 ADK 工具函數，內部連接 MCP 伺服器
"""
import asyncio
import os
import requests
from typing import Dict, Any

# MCP 連接設置
MCP_SERVER_PATH = '/Volumes/Ketomuffin_mac/AI/mcpserver/mcp-stock-ta'
PYTHON_INTERPRETER = os.path.join(MCP_SERVER_PATH, '.venv/bin/python')
SERVER_SCRIPT = os.path.join(MCP_SERVER_PATH, 'server.py')

# 全局 MCP 連接（延遲初始化）
_mcp_connection = None
_connection_lock = asyncio.Lock()

async def _get_mcp_connection():
    """獲取或創建 MCP 連接"""
    global _mcp_connection
    
    if _mcp_connection is None:
        async with _connection_lock:
            if _mcp_connection is None:
                try:
                    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
                    
                    tools, exit_stack = await MCPToolset.from_server(
                        connection_params=StdioServerParameters(
                            command=PYTHON_INTERPRETER,
                            args=[SERVER_SCRIPT],
                            env={'TIINGO_API_KEY': os.environ.get('TIINGO_API_KEY', '2146105fde5488455a958c98755941aafb9d9c66')}
                        )
                    )
                    
                    # 將工具轉換為字典以便快速查找
                    tool_dict = {}
                    for tool in tools:
                        tool_dict[tool.name] = tool
                    
                    _mcp_connection = {'tools': tool_dict, 'exit_stack': exit_stack}
                    print(f"✅ MCP 連接已建立，可用工具: {list(tool_dict.keys())}")
                    
                except Exception as e:
                    print(f"❌ MCP 連接失敗: {e}")
                    _mcp_connection = {'tools': {}, 'exit_stack': None}
    
    return _mcp_connection

def get_stock_price(ticker: str) -> Dict[str, Any]:
    """
    獲取股票當前價格和基本信息
    
    Args:
        ticker: 股票代碼 (例如 "AAPL", "TSLA", "GOOGL")
    
    Returns:
        包含股票價格信息的字典
    """
    try:
        # 檢查是否已有運行中的 event loop
        try:
            loop = asyncio.get_running_loop()
            # 如果有運行中的 loop，使用 run_in_executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_sync_get_stock_price, ticker)
                return future.result()
        except RuntimeError:
            # 沒有運行中的 loop，創建新的
            return _sync_get_stock_price(ticker)
        
    except Exception as e:
        return {
            "error": f"獲取股價失敗: {str(e)}",
            "ticker": ticker
        }

def _sync_get_stock_price(ticker: str) -> Dict[str, Any]:
    """同步版本的獲取股價函數"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _async_call():
            connection = await _get_mcp_connection()
            if 'get_stock_price' in connection['tools']:
                tool = connection['tools']['get_stock_price']
                return await tool(ticker=ticker)
            else:
                return {"error": "get_stock_price 工具不可用", "ticker": ticker}
        
        result = loop.run_until_complete(_async_call())
        loop.close()
        
        return result
        
    except Exception as e:
        return {
            "error": f"獲取股價失敗: {str(e)}",
            "ticker": ticker
        }

def get_technical_indicators(ticker: str, indicators: str = "SMA,EMA,RSI,MACD", time_period: str = "365d") -> Dict[str, Any]:
    """
    計算股票技術指標
    
    Args:
        ticker: 股票代碼 (例如 "AAPL", "TSLA")
        indicators: 技術指標，逗號分隔 (例如 "SMA,EMA,RSI,MACD")
        time_period: 時間範圍 (例如 "90d", "180d", "1y")
    
    Returns:
        包含技術指標分析結果的字典
    """
    try:
        # 運行異步函數
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _async_call():
            connection = await _get_mcp_connection()
            if 'get_technical_indicators' in connection['tools']:
                tool = connection['tools']['get_technical_indicators']
                # 轉換指標字符串為列表
                indicator_list = [ind.strip() for ind in indicators.split(',')]
                return await tool(ticker=ticker, indicators=indicator_list, time_period=time_period)
            else:
                return {"error": "get_technical_indicators 工具不可用", "ticker": ticker}
        
        result = loop.run_until_complete(_async_call())
        loop.close()
        
        return result
        
    except Exception as e:
        return {
            "error": f"技術指標分析失敗: {str(e)}",
            "ticker": ticker,
            "indicators": indicators
        }

def get_momentum_analysis(ticker: str, time_period: str = "180d") -> Dict[str, Any]:
    """
    進行股票動量分析
    
    Args:
        ticker: 股票代碼 (例如 "AAPL", "TSLA")
        time_period: 分析時間範圍 (例如 "90d", "180d", "1y")
    
    Returns:
        包含動量分析結果的字典
    """
    try:
        # 運行異步函數
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _async_call():
            connection = await _get_mcp_connection()
            if 'get_momentum_stock_analysis' in connection['tools']:
                tool = connection['tools']['get_momentum_stock_analysis']
                return await tool(ticker=ticker, time_period=time_period)
            else:
                return {"error": "get_momentum_stock_analysis 工具不可用", "ticker": ticker}
        
        result = loop.run_until_complete(_async_call())
        loop.close()
        
        return result
        
    except Exception as e:
        return {
            "error": f"動量分析失敗: {str(e)}",
            "ticker": ticker,
            "time_period": time_period
        }

def list_available_indicators() -> Dict[str, Any]:
    """
    列出所有可用的技術指標
    
    Returns:
        包含可用指標說明的字典
    """
    try:
        # 運行異步函數
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _async_call():
            connection = await _get_mcp_connection()
            if 'list_available_indicators' in connection['tools']:
                tool = connection['tools']['list_available_indicators']
                return await tool()
            else:
                return {"error": "list_available_indicators 工具不可用"}
        
        result = loop.run_until_complete(_async_call())
        loop.close()
        
        return result
        
    except Exception as e:
        return {
            "error": f"列出指標失敗: {str(e)}"
        }
