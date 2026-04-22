from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.celery_app import run_full_pipeline
from app.utils import verify_jwt
import uuid

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/research")
@limiter.limit("10/minute")
async def start_research(request: Request, query: str, token: str = Depends(verify_jwt)):
    user_id = token  # 从JWT获取
    thread_id = str(uuid.uuid4())
    task = run_full_pipeline.delay(query, user_id, thread_id)
    return {"task_id": task.id, "thread_id": thread_id}