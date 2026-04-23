from langchain_openai import ChatOpenAI   
from app.metrics import record_llm_usage

llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",  # vLLM服务地址（双4090 tensor-parallel-size=2）
    api_key="EMPTY",
    model="/data/Qwen2.5-14B-Instruct"
)
async def critic_node(state):
    prompt = f"严格评估报告质量并给出改进意见：{state.get('draft', '')}"
    critique = await llm.ainvoke(prompt)
    if hasattr(critique, 'usage') and critique.usage:
        record_llm_usage(
            tokens=critique.usage.total_tokens, 
            model="/data/Qwen2.5-14B-Instruct"    
        )
    return {"critique": critique.content, "messages": [critique]}
