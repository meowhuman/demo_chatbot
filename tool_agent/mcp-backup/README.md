# Tool Agent 與 deer-flow 集成指南

## 概述

本專案將 Google ADK (Agent Development Kit) 的工具代理與 deer-flow 深度研究框架進行了集成。通過 MCP (Multimodal Capability Protocol) 協議，我們實現了對 deer-flow 功能的無縫調用，讓代理能夠執行深度研究任務。

## 功能特點

- **深度研究能力**：利用 deer-flow 執行詳盡的網路研究，生成全面的報告
- **異步架構**：採用 Python 異步設計，實現高效的工具調用
- **MCP 協議支持**：通過標準的 MCP 協議實現多模態能力擴展
- **多工具集成**：結合股票分析、加密貨幣分析和深度研究等多種工具

## 安裝與配置

### 前置需求

- Python 3.8+
- Google ADK 套件
- deer-flow 專案（位於 `/Volumes/Ketomuffin_mac/AI2/deer-flow`）

### 安裝步驟

1. 確保 deer-flow 專案已正確安裝
   ```bash
   cd /Volumes/Ketomuffin_mac/AI2/deer-flow
   pip install -e .
   ```

2. 安裝本專案依賴
   ```bash
   cd /Volumes/Ketomuffin_mac/AI2/A2A_agent/2-tool-agent
   pip install -e .
   ```

## 使用方法

啟動 Tool Agent 服務：

```bash
cd /Volumes/Ketomuffin_mac/AI2/A2A_agent/2-tool-agent
python -m tool_agent
```

使用 ADK CLI 工具與代理交互：

```bash
adk web
```

## 深度研究功能示例

在與代理交談時，您可以使用以下類型的查詢來觸發深度研究功能：

- "研究量子計算對密碼學的影響"
- "幫我分析元宇宙的發展趨勢"
- "深入調查人工智能在醫療領域的應用"

## 技術架構

本專案採用以下架構：

1. **Tool Agent**：基於 Google ADK 的代理框架
2. **MCP 封裝**：封裝 deer-flow 為標準 MCP 協議服務
3. **異步調用層**：管理與 MCP 服務的通信
4. **多工具集成**：整合多個功能專用工具

## 注意事項

- 確保 deer-flow 的路徑配置正確
- 異步操作需要在支持異步的環境中運行
- MCP 服務需要保持運行以支持工具調用

## 故障排除

如果遇到問題，請檢查：

1. deer-flow 專案是否能正常獨立運行
2. MCP 服務是否已啟動並正確連接
3. 工具路徑配置是否正確

## 聯繫方式

如需幫助或報告問題，請聯繫專案維護者。
