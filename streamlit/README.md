# KM 股票技術分析助手 - Streamlit 版本 📈

這是 KM 股票技術分析工具的 Streamlit 前端介面，提供了一個友好的聊天界面來訪問股票技術分析功能。

## 功能特色 🚀

- **互動式聊天界面** - 直接與股票分析 AI 聊天
- **快速選擇工具** - 側邊欄提供常用股票和分析類型
- **即時股票分析** - 使用真實市場數據進行分析
- **技術指標支持** - SMA, EMA, RSI, MACD 等
- **動能分析** - 綜合多指標評估股票動能
- **成交量分析** - 包括 VWAP, OBV 等成交量指標

## 安裝說明 ⚙️

1. 確保你已安裝所需的依賴項：
```bash
pip install -r requirements.txt
```

2. 設置 API 密鑰：
   - 創建 `.streamlit/secrets.toml` 文件並添加你的 Tiingo API 密鑰：
   ```toml
   [api_keys]
   TIINGO_API_KEY = "你的_TIINGO_API_密鑰"
   ```

3. 運行 Streamlit 應用：
```bash
streamlit run app.py
```

## 部署到 Streamlit Cloud 🌐

1. 將代碼推送到 GitHub 存儲庫
2. 訪問 [Streamlit Cloud](https://streamlit.io/cloud)
3. 點擊 "New app" 並連接你的 GitHub 存儲庫
4. 配置應用設置，包括 API 密鑰等秘密
5. 部署應用

## 使用方法 💬

1. 在側邊欄選擇一個股票和分析類型，然後點擊 "執行分析"
2. 或者在聊天輸入框中直接輸入你的問題，例如：
   - "分析 TSLA 的 RSI 和 MACD 指標"
   - "AAPL 的動能分析如何？"
   - "查詢 MSFT 的最新股價"
   - "分析 NVDA 的成交量"

## 數據來源 📊

股票數據來自 Tiingo API，提供高質量的金融市場數據。你需要一個 Tiingo API 密鑰來使用此應用。可以在 [Tiingo 網站](https://api.tiingo.com/) 上註冊獲取免費的 API 密鑰。

## 文件結構 📁

```
KM-stock-ta-streamlit/
├── app.py                  # 主要 Streamlit 應用
├── mcp_tools/              # 簡化版股票分析工具
│   ├── __init__.py
│   └── stock_tools.py
├── .streamlit/             # Streamlit 配置
│   ├── config.toml
│   └── secrets.toml
├── requirements.txt        # 依賴項
└── README.md               # 本文件
```

## 注意事項 ⚠️

- 本工具僅供教育和研究目的使用
- 投資決策應基於多種因素，不應僅依賴技術分析
- 過往表現不代表未來結果

---

*版本: 1.0.0*  
*最後更新: 2025-06-03*
