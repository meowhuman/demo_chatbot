# KM Tool Agent Test - Stock Technical Analysis 📈

呢個係一個整合咗股票技術分析 MCP 工具嘅 ADK agent。佢提供全面嘅股票分析功能，包括技術指標、動能分析、回測同策略優化。

## 功能特色 🚀

### 📊 技術指標分析
- **移動平均線**: SMA, EMA
- **動能指標**: RSI, MACD, ADX, ATR
- **波幅指標**: 布林帶, CCI
- **趨勢指標**: 隨機指標, Williams %R

### 🎯 動能分析
- 綜合動能評分 (0-100)
- 多重技術指標確認
- 突破點識別
- 過度買賣保護

### 📈 回測功能
- MA Crossover 策略
- RSI 策略
- MACD 策略  
- Bollinger Bands 策略

### 🔍 策略優化
- 參數優化
- 績效評估
- 風險分析

### 🔎 數據品質檢查
- 數據完整性檢查
- 準確性驗證

## 架構設計 🏗️

呢個 agent 使用咗 **MCP (Model Context Protocol)** 嚟連接外部嘅股票技術分析工具：

```
KM-tool-agent-test/
├── tool_agent/
│   ├── __init__.py          # Package 初始化
│   ├── agent.py             # 主要 agent 邏輯 (MCP 連接)
│   ├── .env                 # API 密鑰配置
│   └── tools/               # 空目錄 (用緊 MCP 工具)
│       └── __init__.py
└── README.md                # 呢個檔案
```

## MCP 工具連接 🔗

Agent 連接到位於 `/Volumes/Ketomuffin_mac/AI/mcpserver/mcp-stock-ta` 嘅 MCP 伺服器，提供以下工具：

- `get_technical_indicators`: 計算技術指標
- `get_momentum_stock_analysis`: 動能分析
- `run_simple_backtest`: 簡單回測
- `advanced_strategy_optimization_fixed`: 策略優化
- `get_data_quality_report`: 數據品質檢查

## 環境配置 ⚙️

確保你嘅 `.env` 檔案包含以下 API 密鑰：

```env
GOOGLE_API_KEY=your_google_api_key_here
TIINGO_API_KEY=your_tiingo_api_key_here
```

## 使用方法 💡

```python
from tool_agent import root_agent

# Agent 會自動連接到 MCP 伺服器並載入工具
# 你可以詢問股票分析相關問題，例如：
# - "分析 AAPL 嘅技術指標"
# - "Tesla 嘅動能評分係幾多？"
# - "用 MA crossover 策略回測 NVDA"
```

## 特點 ✨

- **🔄 自動重試機制**: 連接失敗時會自動重試
- **📝 繁體中文支援**: 所有分析結果都用繁體中文呈現
- **⚠️ 風險警告**: 自動包含投資風險提醒
- **🎯 智能分析**: 提供清晰易明嘅技術指標解釋

## 依賴項目 🛠️

- Google ADK
- MCP (Model Context Protocol)
- Python 3.10+
- Tiingo API (用於股票數據)

---

*建立日期: 2025-06-02*  
*基於: /Volumes/Ketomuffin_mac/AI2/agents-mcp-test/stock_ta 參考*
