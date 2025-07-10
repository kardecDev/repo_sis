# infrastructure/security/rate_limiter.py
import redis.asyncio as redis
from domain.ports import RateLimiterPort

class RedisRateLimiter(RateLimiterPort):
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        current = await self.redis.get(key)
        if current is None:
            return False
        return int(current) >= limit

    async def increment_counter(self, key: str, window: int) -> int:
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        return results[0]