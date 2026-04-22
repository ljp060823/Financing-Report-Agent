from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from app.routers.research import start_research as research_router
from app.metrics import record_cache_hit, record_cache_miss 
from app.utils import logger
import json
from app.graph.builder import graph

app = FastAPI(title="financial agent")
app.include_router(research_router, prefix="/api")

@app.middleware("http")
async def monitor_concurrency(request: Request, call_next):
    record_cache_hit()
    try:
        return await call_next(request)
    finally:
        record_cache_miss()

@app.post("/stream/{thread_id}")
async def stream_events(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    async def event_generator():
        async for chunk in graph.astream_events({"messages": []}, config, version="v2"):
            yield f"data: {json.dumps(chunk)}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

#interrupt，human_feedback