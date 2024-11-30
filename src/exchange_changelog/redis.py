import functools
import os
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


def exists(key: str) -> int:
    return get_redis_client().exists(key)


def set(key: str, value: str | int) -> bool | None:
    return get_redis_client().set(key, value)


def get(key: str) -> Any | None:
    return get_redis_client().get(key)
