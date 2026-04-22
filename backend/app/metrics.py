from prometheus_client import Counter, Gauge, Histogram
import redis

concurrent_requests = Gauge('concurrent_requests', '当前并发数')
llm_token_usage = Histogram('llm_token_usage', 'Token消耗')
celery_queue_length = Gauge('celery_queue_length', 'Celery队列长度')
cache_hit = Counter('cache_hit_total', '缓存命中')
cache_miss = Counter('cache_miss_total', '缓存未命中')

redis_client = redis.from_url("redis://redis:6379/0")

def record_llm_usage(tokens: int, model: str = "/data/Qwen2.5-14B-Instruct"):
    """LLM Token消耗"""
    llm_token_usage.labels(model=model).observe(tokens)

def update_celery_queue_length():
    # 通过Redis获取Celery队列长度
    length = redis_client.llen("agent")  # 自定义队列名字
    celery_queue_length.set(length)

def record_cache_hit():
    cache_hit.inc()

def record_cache_miss():
    cache_miss.inc()