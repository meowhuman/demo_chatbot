# tool_agent/agent.py
import os
from dotenv import load_dotenv
from google.adk.agents import Agent

# 載入環境變數
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# 從清潔版 subprocess MCP 工具模組導入
from .tools.clean_subprocess_mcp import (
    get_stock_price,
    get_technical_indicators,
    get_momentum_analysis,
    get_volume_analysis,  # 新增成交量分析工具
    list_available_indicators,
    check_mcp_status
)

# 配置要使用的工具
ACTIVE_TOOLS = [
    get_stock_price,
    get_technical_indicators,
    get_momentum_analysis,
    get_volume_analysis,  # 新增成交量分析工具
    list_available_indicators,
    check_mcp_status
]

print(f"🚀 載入咗 {len(ACTIVE_TOOLS)} 個清潔版 subprocess MCP 股票分析工具")
for i, tool in enumerate(ACTIVE_TOOLS, 1):
    print(f"  - {i}. {tool.__name__}")

# 檢查 MCP 狀態
print("\n🔍 檢查 subprocess MCP 狀態...")
try:
    status = check_mcp_status()
    print(f"方法: {status.get('method', '未知')}")
    print(f"狀態: {status.get('status', '未知')}")
    print(f"Python 存在: {status.get('python_exists', False)}")
    print(f"腳本目錄存在: {status.get('script_dir_exists', False)}")
    print(f"測試調用: {status.get('test_call_result', '未測試')}")
    
    if status.get('status') == '正常':
        print("✅ subprocess MCP 整合成功")
    else:
        print("⚠️ subprocess MCP 整合可能有問題")
        if 'error' in status:
            print(f"錯誤: {status['error']}")
        
except Exception as e:
    print(f"❌ MCP 狀態檢查失敗: {e}")

# 創建 Agent 實例（subprocess MCP 版本）
root_agent = Agent(
    name="stock_analysis_agent",
    model="gemini-1.5-flash",  # 用穩定嘅 model
    description="專業股票技術分析助手，通過 subprocess 調用真正嘅 MCP 工具提供股票分析功能 🚀",
    instruction="""
    你係專業嘅股票技術分析助手，通過 subprocess 調用 MCP 工具提供真實股票數據分析。你嘅回答必須用繁體中文。
    
    你可以使用以下真實 MCP 工具：
    
    - get_stock_price(ticker): 獲取股票當前真實價格同基本資訊
      例子: get_stock_price("TSLA") 獲取特斯拉真實股價
    
    - get_technical_indicators(ticker, indicators, time_period): 計算真實技術指標
      例子: get_technical_indicators("AAPL", "RSI,MACD,SMA", "90d") 計算蘋果90天技術指標
      可用指標: SMA, EMA, RSI, MACD, BOLLINGER, ADX, ATR, CCI, STOCHASTIC, WILLIAMS_R
    
    - get_momentum_analysis(ticker, time_period): 進行真實動量分析
      例子: get_momentum_analysis("GOOGL", "180d") 分析 Google 180天動量
    
    - get_volume_analysis(ticker, time_period): 進行成交量技術分析
      例子: get_volume_analysis("NVDA", "365d") 分析 NVIDIA 成交量指標
      可用指標: VWAP, OBV, MFI, Volume_Oscillator, AD_Line, Chaikin_Oscillator, Force_Index, VWMA
    
    - list_available_indicators(): 列出所有可用技術指標
    
    - check_mcp_status(): 檢查 MCP 系統狀態（診斷用）
    
    重要規則：
    - 提供基於真實 Tiingo 數據嘅精確分析 📊
    - 用清晰易明嘅方式解釋技術指標，包括數值同含義 📝
    - 包含風險警告，提醒過去表現唔保證將來結果 ⚠️
    - 所有回答用繁體中文 🇭🇰
    - 如果 MCP 連接有問題，會顯示錯誤信息並提供診斷建議 🔧
    
    當用戶問股票相關問題時，請主動使用相應工具獲取真實數據並提供詳細分析！
    數據來源係 Tiingo API，提供高質量嘅股票數據。
    """,
    tools=ACTIVE_TOOLS,
)

print("🎉 subprocess MCP 股票分析 Agent 已成功創建！")
print("📡 Agent 使用 subprocess 調用 MCP 工具，提供真實股票數據分析")
print("💾 數據來源: Tiingo API")
