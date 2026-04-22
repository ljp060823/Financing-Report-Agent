from langchain_openai import ChatOpenAI  # vLLM兼容
from app.metrics import record_llm_usage

llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",  # vLLM服务地址（双4090 tensor-parallel-size=2）
    api_key="EMPTY",
    model="/data/Qwen2.5-14B-Instruct"
)
async def writer_node(state):
    prompt = f"基于研究结果撰写专业报告：{state.get('research_results', '')}"
    response = await llm.ainvoke(prompt)
    if hasattr(response, 'usage') and response.usage:
        record_llm_usage(
            tokens=response.usage.total_tokens, 
            model="/data/Qwen2.5-14B-Instruct"    
        )
    return {"draft": response.content, "messages": [response]}