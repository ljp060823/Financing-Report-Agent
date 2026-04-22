import gradio as gr
import requests
import json
import httpx   # 推荐使用 httpx 支持 SSE

async def chat(message: str, history):
    # research启动任务
    resp = requests.post(
        "http://localhost:8000/api/research",
        json={"query": message},
        # headers={"Authorization": "Bearer your-jwt-token"}  # 生产环境需要带 JWT
    )
    if resp.status_code != 200:
        yield "启动任务失败，请检查后端"
        return
    
    data = resp.json()
    thread_id = data["thread_id"]
    yield f"任务已启动！thread_id: {thread_id}\n正在研究中...\n"

    #流式接口实时接收输出
    url = f"http://localhost:8000/stream/{thread_id}"
    
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        chunk = json.loads(line[6:])   # 去掉 "data: "
                        # 根据 LangGraph astream_events 的结构提取内容
                        if "data" in chunk and isinstance(chunk["data"], dict):
                            content = chunk["data"].get("chunk", {}).get("content", "")
                            if content:
                                yield content
                        elif "message" in chunk:
                            yield str(chunk["message"])
                    except:
                        continue  

# 启动
gr.ChatInterface(
    fn=chat,
    title="AetherReport - 企业级多Agent研究报告生成",
    description="输入研究主题，实时观看研究 → 图谱推理 → 写作 → 批评迭代 → PDF生成全过程",
    concurrency_limit=10
).launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False
)