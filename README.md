# KM Stock Technical Analysis Agent

This repository contains a Stock Technical Analysis Agent built with Google ADK and a Streamlit web frontend for easy interaction.

## Repository Structure

- `/tool_agent/`: Contains the ADK agent for stock technical analysis
- `/scripts/`: Helper scripts for the agent
- `/streamlit/`: Streamlit web application for interacting with the agent

## Stock Technical Analysis Agent

The agent provides comprehensive stock analysis capabilities:

- Technical indicators (SMA, EMA, RSI, MACD, etc.)
- Momentum analysis with scoring
- Volume analysis
- Stock price information

## Streamlit Web App

The Streamlit application provides a chat interface to interact with the stock analysis capabilities:

### Features

- Interactive chat interface
- Quick selection sidebar for common stocks and analysis types
- Real-time stock data analysis
- Technical indicators support
- Momentum analysis with scoring
- Volume analysis

### Usage

To run the Streamlit app locally:

```bash
cd streamlit
./run_local.sh
```

Or visit the deployed version at: [https://demochatbot-ta.streamlit.app/](https://demochatbot-ta.streamlit.app/)

## Deployment

The Streamlit app can be deployed directly from this repository. Just point Streamlit Cloud to the `streamlit/app.py` file.

## 關於安全性的說明

### API 密鑰處理

為了確保 API 密鑰的安全，請遵循以下步驟：

1. 永遠不要在代碼中直接硬編碼 API 密鑰
2. 使用 `.env` 文件存儲環境變數（參考 `.env.example` 文件）
3. 確保 `.env` 文件已添加到 `.gitignore` 中，避免提交到版本控制系統
4. 使用環境變數載入 API 密鑰：`os.environ.get('API_KEY_NAME')`

### 設置說明

1. 複製 `.env.example` 文件為 `.env`：
```bash
cp tool_agent/.env.example tool_agent/.env
```

2. 編輯 `.env` 文件，添加您的 API 密鑰：
```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_google_api_key_here
TIINGO_API_KEY=your_tiingo_api_key_here
```

3. 確保 `.env` 不會被提交到 Git：
```bash
echo "tool_agent/.env" >> .gitignore
```

### 安全檢查

在提交代碼前，請執行以下安全檢查：

1. 確認沒有硬編碼的密鑰或敏感資訊
2. 確認 `.env` 文件不會被提交
3. 考慮使用工具如 GitGuardian 來監控潛在的密鑰洩露

## License

MIT License
