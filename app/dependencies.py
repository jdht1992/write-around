from fastapi import Depends
from typing import AsyncGenerator
import redis
from typing_extensions import Annotated
from app.databases import async_session
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.redis import get_redis


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    If you don't close the session, connection never returns to the pool, 
    and you can run out of connections.
    """
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[redis.Redis, Depends(get_redis)]
