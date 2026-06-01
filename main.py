import json
import time

from app.dependencies import SessionDep, RedisDep
from app.models import Item
from app.schemas import ItemSchema, ItemUpdateSchema

from fastapi import FastAPI, HTTPException, Request

from app.lifespan import lifespan


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/items/")
async def create_item(item: ItemSchema, db: SessionDep):
    """
    WRITE-AROUND: We write only to Postgres. 
    The cache is not updated here.
    """
    new_item = Item(name=item.name, description=item.description)

    db.add(new_item)
    await db.commit()

    return new_item.model_dump()


@app.patch("/items/{item_id}")
async def update_item_by_id(item_id: int, item: ItemUpdateSchema, db: SessionDep):
    item_obj = await db.get(Item, item_id)

    if not item_obj:
        raise HTTPException(status_code=404, detail="Item not found.")

    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(item_obj, key, value)

    db.add(item_obj)
    await db.commit()
    await db.refresh(item_obj)

    return item_obj.model_dump()


@app.get("/items/{item_id}")
async def read_item(item_id: int, db: SessionDep, redis: RedisDep) -> dict:
    """
    Write-Around with Redis

    READ-AROUND logic: Check Redis -> Check Postgres -> Populate Redis
    """

    # 1. Check Redis with AWAIT
    if (cached := await redis.get(f"item:{item_id}")):
        return {"source": "cache", "data": json.loads(cached)}
    
    # If not in cache, read from Postgres using AsyncSession.get for primary key lookup
    if not (db_item := await db.get(Item, item_id)):
        raise HTTPException(status_code=404, detail="Item not found")

    # Populate Redis cache for future requests
    await redis.setex(f"item:{item_id}", 300, json.dumps(db_item.dict()))

    return {"source": "database", "data": db_item.dict()}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    
    print(f"Ruta: {request.url.path} | Tiempo: {process_time:.4f} seg")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
