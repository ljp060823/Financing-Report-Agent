from celery import Celery
import redis
import json
from datetime import datetime, timedelta
from app.graph.builder import build_graph
from app.metrics import update_celery_queue_length, record_cache_hit, record_cache_miss

celery_app = Celery("agent", broker="redis://redis:6379/0", backend="redis://redis:6379/0")
redis_client = redis.from_url("redis://redis:6379/0")

@celery_app.task(bind=True, max_retries=3)
def run_full_pipeline(self, query: str, user_id: str, thread_id: str):
    update_celery_queue_length()
    cache_key = f"report:{hash(query)}:{user_id}"
    if cached := redis_client.get(cache_key):
        record_cache_hit()
        return json.loads(cached)
    record_cache_miss()
    config = {"configurable": {"thread_id": thread_id}}
    graph = build_graph()
    result = graph.invoke({"messages": [("human", query)], "user_id": user_id}, config)
    redis_client.setex(cache_key, 7200, json.dumps(result))
    return result

@celery_app.task
def clean_old_cache():
    now = datetime.now()
    for key in list(redis_client.scan_iter("report:*")):
        ttl = redis_client.ttl(key)
        if ttl < 0 or datetime.fromtimestamp(now.timestamp() - ttl) < now - timedelta(hours=24):
            redis_client.delete(key)

@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(3600, clean_old_cache.s(), name='clean cache every hour')