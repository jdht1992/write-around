from contextlib import asynccontextmanager
import json
import time

from app.databases import get_session
from app.models import Item
from app.schemas import ItemSchema

from fastapi import Depends, FastAPI, HTTPException, Request
from app.databases import create_all_tables

from app.redis import redis_client

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_all_tables()
    yield

app = FastAPI(lifespan=lifespan_handler)


@app.post("/items/")
async def create_item(item: ItemSchema, db: AsyncSession = Depends(get_session)):
    """
    WRITE-AROUND: We write only to Postgres. 
    The cache is not updated here.
    """
    new_item = Item(name=item.name, description=item.description)

    db.add(new_item)
    await db.commit()

    return new_item.dict()

@app.get("/items/{item_id}")
async def read_item(item_id: int, db: AsyncSession = Depends(get_session)) -> dict:
    """
    Write-Around with Redis

    READ-THROUGH logic: Check Redis -> Check Postgres -> Populate Redis
    """

    # 1. Check Redis with AWAIT
    if (cached := await redis_client.get(f"item:{item_id}")):
        return {"source": "cache", "data": json.loads(cached)}
    
    # If not in cache, read from Postgres using AsyncSession.get for primary key lookup
    if not (db_item := await db.get(Item, item_id)):
        raise HTTPException(status_code=404, detail="Item not found")

    # Populate Redis cache for future requests
    await redis_client.setex(f"item:{item_id}", 300, json.dumps(db_item.dict()))

    return {"source": "database", "data": db_item.dict()}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    
    print(f"Ruta: {request.url.path} | Tiempo: {process_time:.4f} seg")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
