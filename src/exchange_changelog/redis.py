import functools
import os
from typing import Any

import redis.asyncio as redis


@functools.cache
def get_redis_client() -> redis.Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    db = int(os.getenv("REDIS_DB", 0))

    return redis.Redis.from_url(f"redis://{host}:{port}/{db}")


async def exists(key: str) -> Any:
    client = get_redis_client()
    res = await client.exists(key)
    return res


async def set(key: str, value: str | int) -> Any:
    client = get_redis_client()
    res = await client.set(key, value)
    return res


async def get(key: str) -> Any:
    client = get_redis_client()
    res = await client.get(key)
    return res
