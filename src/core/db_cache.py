from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.core.settings import settings


def initiate_redis_cache():
    redis = aioredis.from_url(settings.redis_settings.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="cache")