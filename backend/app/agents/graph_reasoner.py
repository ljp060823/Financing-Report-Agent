from langchain_openai import ChatOpenAI
from app.tools import neo4j_graph_reason
from app.metrics import record_llm_usage

llm = ChatOpenAI(base_url="http://localhost:8001/v1", api_key="EMPTY", model="/data/Qwen2.5-14B-Instruct")

async def graph_reasoner_node(state):
    """GraphReasoner：提取实体 → Neo4j构建 → 多跳事件查询（支持比亚迪式查询）"""
    extract_prompt = f"从以下内容提取公司名称和事件（JSON）：{state['research_results']}"
    extraction = await llm.ainvoke(extract_prompt)
    
    # 存入Neo4j（生产幂等）
    # ...（省略具体MERGE，实际可根据extraction动态插入）
    company = await llm.ainvoke("从问题提取公司名：" + state["question"])
    if hasattr(company, 'usage') and company.usage:
        record_llm_usage(
            tokens=company.usage.total_tokens, 
            model="/data/Qwen2.5-14B-Instruct"    
        )
    # 使用你提供的Cypher风格查询
    insight = await neo4j_graph_reason.ainvoke(company)  # 可动态
    return {"graph_results": insight, "messages": [insight]}
