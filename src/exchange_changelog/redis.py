import functools
import os
from collections.abc import Awaitable
from typing import Any

import redis


@functools.cache
def get_redis_client() -> redis.Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    db = int(os.getenv("REDIS_DB", 0))
    return redis.Redis(
        host=host,
        port=port,
        db=db,
        charset="utf-8",
        decode_responses=True,
    )


def exists(key: str) -> Awaitable[Any] | Any:
    client = get_redis_client()
    res = client.exists(key)
    return res


def set(key: str, value: str | int) -> Awaitable[Any] | Any:
    client = get_redis_client()
    res = client.set(key, value)
    return res


def get(key: str) -> Awaitable[Any] | Any:
    client = get_redis_client()
    res = client.get(key)
    return res
