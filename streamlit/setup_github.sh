#!/bin/bash
# 初始化 Git 存儲庫並準備推送到 GitHub

# 切換到 Streamlit 應用目錄
cd /Volumes/Ketomuffin_mac/ADK/agent-development-kit/KM-stock-ta-streamlit

# 初始化 Git 存儲庫
git init

# 添加所有文件
git add .

# 初次提交
git commit -m "初始化股票技術分析 Streamlit 應用"

# 添加遠程倉庫
echo "請輸入您的 GitHub 存儲庫 URL (例如: https://github.com/username/repo.git):"
read repo_url

git remote add origin $repo_url

# 切換到 main 分支
git branch -M main

# 推送到 GitHub
echo "準備推送到 GitHub，請確保您已登錄 GitHub..."
git push -u origin main

echo "完成! 您的 Streamlit 應用已推送到 GitHub。"
echo "接下來您可以訪問 https://streamlit.io/cloud 並連接您的 GitHub 存儲庫來部署應用。"
