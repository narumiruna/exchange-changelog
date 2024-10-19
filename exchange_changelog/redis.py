import functools
import os

import redis


@functools.cache
def get_redis_client() -> redis.Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", 6379)
    db = os.getenv("REDIS_DB", 0)
    return redis.Redis(host=host, port=port, db=db)


def exists(key: str) -> int:
    return get_redis_client().exists(key)


def set(key: str, value: str) -> bool:
    return get_redis_client().set(key, value)
