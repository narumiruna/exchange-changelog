import functools
import os
from collections.abc import Awaitable
from typing import Any

import redis


@functools.cache
def get_redis_client() -> redis.Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", 6379)
    db = os.getenv("REDIS_DB", 0)
    return redis.Redis(
        host=host,
        port=port,
        db=db,
        charset="utf-8",
        decode_responses=True,
    )


def exists(key: str) -> Awaitable[Any] | int:
    return get_redis_client().exists(key)


def set(key: str, value: str | int) -> Awaitable[Any] | bool:
    return get_redis_client().set(key, value)


def get(key: str) -> Awaitable[Any] | str:
    return get_redis_client().get(key)
