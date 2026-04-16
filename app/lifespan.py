from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.databases import create_all_tables
from app.redis import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await get_redis()
    await create_all_tables()
    yield
    await app.state.redis.close()    
