import aiohttp
from langchain.tools import tool
from weasyprint import HTML
from app.db import graph_db, embeddings
from langchain.agents import create_agent, Tool
import numpy as np
from langchain_core.tools import tool
import requests
import os


BOCHA_API_KEY = os.getenv("BOCHA_API_KEY")  # 从环境变量获取API密钥
@tool
def bocha_websearch_tool(query: str, count: int = 10) -> str:
    """
    使用Bocha Web Search API 进行网页搜索。

    参数:
    - query: 搜索关键词
    - freshness: 搜索的时间范围
    - summary: 是否显示文本摘要
    - count: 返回的搜索结果数量

    返回:
    - 搜索结果的详细信息，包括网页标题、网页URL、网页摘要、网站名称、网站Icon、网页发布时间等。
    """
    
    url = 'https://api.bochaai.com/v1/web-search'
    headers = {
        'Authorization': f'Bearer {BOCHA_API_KEY}',  # 请替换为你的API密钥
        'Content-Type': 'application/json'
    }
    data = {
        "query": query,
        "freshness": "noLimit", # 搜索的时间范围，例如 "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"
        "summary": True, # 是否返回长文本摘要
        "count": count
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        json_response = response.json()
        try:
            if json_response["code"] != 200 or not json_response["data"]:
                return f"搜索API请求失败，原因是: {response.msg or '未知错误'}"
            
            webpages = json_response["data"]["webPages"]["value"]
            if not webpages:
                return "未找到相关结果。"
            formatted_results = ""
            for idx, page in enumerate(webpages, start=1):
                formatted_results += (
                    f"引用: {idx}\n"
                    f"标题: {page['name']}\n"
                    f"URL: {page['url']}\n"
                    f"摘要: {page['summary']}\n"
                    f"网站名称: {page['siteName']}\n"
                    f"网站图标: {page['siteIcon']}\n"
                    f"发布时间: {page['dateLastCrawled']}\n\n"
                )
            return formatted_results.strip()
        except Exception as e:
            return f"搜索API请求失败，原因是：搜索结果解析失败 {str(e)}"
    else:
        return f"搜索API请求失败，状态码: {response.status_code}, 错误信息: {response.text}"


@tool
async def neo4j_graph_reason(query: str) -> str:
    """GraphReasoner - 使用你提供的比亚迪查询示例风格（Neo4j 4.4.48）"""
    # 支持动态查询（类似你图片中的比亚迪事件查询）
    cypher = """
    MATCH (c:Company)-[r:HAPPEN]->(e)
    WHERE c.name CONTAINS $company_name
    RETURN c.name as name, r.title as title, e.name as event
    LIMIT 10
    """
    # 生产中可让LLM先提取company_name，这里简化示例
    results = await graph_db.query(cypher, {"company_name": query})
    return str(results)

@tool
def generate_pdf(report_content: str, filename: str = "report.pdf") -> str:
    """生成PDF报告Tool（生产导出）"""
    html_content = f"""
    <h1 style="text-align:center">AetherReport 研究报告</h1>
    <p style="white-space: pre-wrap">{report_content}</p>
    <hr>
    <p>生成时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    """
    HTML(string=html_content).write_pdf(filename)
    return f"PDF生成成功: {filename}"