import asyncio
import logging
import redis.asyncio as redis
from .config import REDIS_HOST, REDIS_PORT

redis_client: redis.Redis | None = None
logger = logging.getLogger("uvicorn")
agent = "redisclient"


async def init_redis():
    global redis_client
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    logger.info(f"{agent}-Redis connected.")


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info(f"{agent}-Redis connection closed.")


async def get_redis():
    global redis_client
    while not redis_client:
        await asyncio.sleep(.1)
    return redis_client