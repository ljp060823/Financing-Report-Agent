from langchain.agents import create_agent,Tool
from langchain_openai import ChatOpenAI
from app.tools import bocha_websearch_tool,neo4j_graph_reason
from app.metrics import record_llm_usage

llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
    model="/data/Qwen2.5-14B-Instruct"
)
bocha_tool = Tool(
    name="BochaWebSearch",
    func=bocha_websearch_tool,
    description="使用Bocha Web Search API 进行搜索互联网网页，输入应为搜索查询字符串，输出将返回搜索结果的详细信息，包括网页标题、网页URL、网页摘要、网站名称、网站Icon、网页发布时间等。"
)
tools = [bocha_tool, neo4j_graph_reason]
agent = create_agent(llm, tools,async_mode=True)

async def researcher_node(state):
    result = await agent.ainvoke({"messages": state["messages"]})
    if hasattr(result, 'usage') and result.usage:
        record_llm_usage(
            tokens=result.usage.total_tokens,
            model="/data/Qwen2.5-14B-Instruct"
        )
    return {"research_results": result["messages"], "messages": result["messages"]}