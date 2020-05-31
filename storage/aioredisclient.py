import asyncio
import aioredis


class AioRedisClient:
    def __init__(self, redis_url, redis_pool_min=5, redis_pool_max=10, loop=None):
        self.redis_url = redis_url
        self.redis_pool_min = redis_pool_min
        self.redis_pool_max = redis_pool_max
        self.pool = None
        self.loop = loop or asyncio.get_event_loop()

    async def create_redis_pool(self):
        self.pool = await aioredis.create_redis_pool(
            self.redis_url,
            minsize=self.redis_pool_min,
            maxsize=self.redis_pool_max,
            loop=self.loop
        )
        return self.pool

    async def destory_redis_pool(self):
        if self.pool is None:
            return
        self.pool.close()
        await self.pool.wait_closed()


