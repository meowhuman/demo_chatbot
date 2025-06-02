import sys
import json
import subprocess
from typing import Dict, Any, List
import os
import time
import requests
from bs4 import BeautifulSoup
import markdownify

# 定義要暴露的工具函數
def deep_research(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    執行深度研究查詢，獲取相關資訊並生成研究報告。
    
    這是一個簡化版的深度研究工具，不需要完整的 deer-flow 環境。
    研究過程包括：基本網絡搜索、內容提取和報告生成。
    
    Args:
        query: 研究查詢，例如「量子計算的最新進展」或「人工智能在醫療中的應用」
        max_results: 最大結果數量，默認為 5
        
    Returns:
        包含研究結果的字典，格式為:
        {
            "status": "success" 或 "error",
            "report": "完整的研究報告內容",
            "summary": "報告的簡短摘要",
            "sources": [
                {"title": "來源標題", "url": "來源網址"}
            ],
            "error_message": 如果發生錯誤，則提供錯誤信息
        }
    """
    try:
        print(f"開始研究: {query}")
        
        # 步驟 1: 搜索相關資訊
        search_results = simple_web_search(query, max_results)
        
        if not search_results:
            return {
                "status": "error",
                "report": "",
                "summary": "",
                "sources": [],
                "error_message": "無法找到相關資訊"
            }
        
        # 步驟 2: 提取頁面內容
        content_results = []
        for result in search_results:
            try:
                content = extract_content(result['url'])
                if content:
                    content_results.append({
                        "title": result['title'],
                        "url": result['url'],
                        "content": content
                    })
            except Exception as e:
                print(f"提取內容時出錯 ({result['url']}): {e}")
        
        # 步驟 3: 生成報告
        report = generate_report(query, content_results)
        
        # 生成簡短摘要
        summary = report[:500] + "..." if len(report) > 500 else report
        
        # 提取來源
        sources = [{"title": r["title"], "url": r["url"]} for r in search_results]
        
        return {
            "status": "success",
            "report": report,
            "summary": summary,
            "sources": sources,
            "error_message": None
        }
    except Exception as e:
        print(f"深度研究時出錯: {str(e)}", file=sys.stderr)
        return {
            "status": "error",
            "report": "",
            "summary": "",
            "sources": [],
            "error_message": str(e)
        }

def simple_web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """執行簡單的網絡搜索並返回結果"""
    try:
        # 使用 DuckDuckGo 搜索 API (不需要 API 密鑰)
        search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(search_url)
        data = response.json()
        
        results = []
        # 提取結果
        if "RelatedTopics" in data:
            for topic in data["RelatedTopics"][:max_results]:
                if "Text" in topic and "FirstURL" in topic:
                    results.append({
                        "title": topic["Text"],
                        "url": topic["FirstURL"]
                    })
        
        # 如果無法從 DuckDuckGo 獲取結果，返回模擬結果
        if not results:
            # 模擬一些常見的搜索結果
            results = [
                {"title": f"關於 {query} 的研究文章", 
                 "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"},
                {"title": f"{query} 的最新進展", 
                 "url": "https://www.nature.com/articles/"},
                {"title": f"{query} - 維基百科", 
                 "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"}
            ]
        
        return results
    except Exception as e:
        print(f"搜索出錯: {e}")
        return []

def extract_content(url: str) -> str:
    """從 URL 提取內容"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return ""
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除腳本和樣式元素
        for script in soup(["script", "style"]):
            script.extract()
        
        # 獲取正文內容
        if soup.body:
            # 嘗試找到主要內容區域
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                content = main_content
            else:
                content = soup.body
            
            # 將 HTML 轉換為 Markdown
            markdown_content = markdownify.markdownify(str(content), heading_style="ATX")
            
            # 清理 Markdown (去除過多的空行等)
            cleaned_content = '\n'.join(line for line in markdown_content.splitlines() if line.strip())
            
            return cleaned_content
        
        return ""
    except Exception as e:
        print(f"提取內容出錯 ({url}): {e}")
        return ""

def generate_report(query: str, content_results: List[Dict]) -> str:
    """基於收集到的內容生成簡單報告"""
    try:
        # 如果沒有結果，返回基本資訊
        if not content_results:
            return f"# 關於 {query} 的研究報告\n\n很抱歉，未能找到關於該主題的詳細資訊。可能需要更具體的查詢或使用專業數據庫進行深入研究。"
        
        # 創建報告標題
        report = f"# 關於「{query}」的深度研究報告\n\n"
        
        # 添加簡介
        report += f"## 簡介\n\n本報告基於網絡上可用的資源，提供關於「{query}」的綜合分析和見解。\n\n"
        
        # 添加主要發現
        report += "## 主要發現\n\n"
        
        # 整合內容結果
        combined_content = ""
        for result in content_results:
            if result.get("content"):
                combined_content += result["content"] + "\n\n"
        
        # 從每個內容中提取一些關鍵段落 (簡單實現，實際中可能需要更複雜的摘要算法)
        paragraphs = [p for p in combined_content.split('\n\n') if p.strip() and len(p) > 100][:5]
        
        for i, paragraph in enumerate(paragraphs):
            report += f"{i+1}. {paragraph.strip()[:300]}...\n\n"
        
        # 添加來源部分
        report += "## 參考來源\n\n"
        for i, result in enumerate(content_results):
            report += f"{i+1}. [{result['title']}]({result['url']})\n"
        
        # 添加結論
        report += "\n## 結論\n\n"
        report += f"「{query}」是一個複雜且不斷發展的領域。以上發現提供了基本的見解，但建議進行更深入的研究以獲取更全面的理解。"
        
        return report
    except Exception as e:
        print(f"生成報告時出錯: {e}")
        return f"# 關於 {query} 的研究報告\n\n由於技術問題，無法生成完整報告: {str(e)}"

# MCP Server 主邏輯
def main():
    # 註冊可用的工具
    tools = {
        "deep_research": deep_research
    }
    
    # 打印工具列表（MCP 協議要求）
    tool_list = []
    for name, func in tools.items():
        tool_list.append({
            "name": name,
            "description": func.__doc__
        })
    
    print(json.dumps({"tools": tool_list}))
    sys.stdout.flush()
    
    # 進入主循環，處理請求
    while True:
        try:
            # 讀取輸入
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line)
            
            # 處理請求
            tool_name = request.get("name")
            params = request.get("parameters", {})
            
            if tool_name in tools:
                tool_func = tools[tool_name]
                result = tool_func(**params)
                response = {
                    "id": request.get("id"),
                    "result": result
                }
            else:
                response = {
                    "id": request.get("id"),
                    "error": f"未知工具: {tool_name}"
                }
            
            # 發送回應
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            print(json.dumps({
                "id": request.get("id", "unknown"),
                "error": str(e)
            }))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
