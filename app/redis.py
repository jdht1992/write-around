import redis.asyncio as redis
from app.config import settings


async def get_redis():

    pool = redis.ConnectionPool.from_url(
        settings.async_redis_url,
        max_connections=10,         # Set the maximum number of connections in the pool
        socket_timeout=5,           # Set the socket timeout in seconds
        socket_connect_timeout=5,   # Set the connection timeout in seconds
        socket_keepalive=True,      # Enable TCP keepalive
        decode_responses=True,      # Automatically decode responses to strings
    )

    return redis.Redis(connection_pool=pool)
