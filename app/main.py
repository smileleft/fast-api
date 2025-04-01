from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
import aioredis
import os
import json
import logging

from . import models, schemas, crud
from .database import engine, get_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL")
redis = None
logger = logging.getLogger("uvicorn")

@app.on_event("startup")
async def startup():
    global redis
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    logger.info("Application startup complete. Redis and DB initialized.")

@app.get("/items/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    cached_item = await redis.get(f"item:{item_id}")
    if cached_item:
        logger.info(f"Cache hit for item {item_id}")
        return json.loads(cached_item)

    logger.info(f"Cache miss for item {item_id}, querying DB...")
    item = await crud.get_item(db, item_id)
    if not item:
        logger.warning(f"Item {item_id} not found in DB.")
        raise HTTPException(status_code=404, detail="Item not found")

    await redis.set(f"item:{item_id}", json.dumps(schemas.Item.from_orm(item).dict()), ex=60)
    logger.info(f"Item {item_id} cached in Redis.")
    return item

@app.post("/items/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    created_item = await crud.create_item(db, item)
    await redis.delete(f"item:{created_item.id}")
    logger.info(f"Item {created_item.id} created and cache invalidated.")
    return created_item

