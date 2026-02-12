import redis.asyncio as redis

REDIS_URL = "redis://redis:6379/0"

redis_pool = redis.ConnectionPool.from_url(
    REDIS_URL, 
    decode_responses=True, 
    max_connections=5
)

redis_client = redis.Redis(connection_pool=redis_pool)
