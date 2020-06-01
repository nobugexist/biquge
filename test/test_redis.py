import asyncio

from storage.aioredisclient import AioRedisClient
from storage.redisclient import RedisClient
from config.config import *


async def test_redis():
    redis = AioRedisClient(REDIS_URL)
    pool = await redis.create_redis_pool()
    for i in range(1000000):
        await pool.sadd("testts",i)
        print(i)

    await redis.destory_redis_pool()

if __name__ == '__main__':
    asyncio.run( test_redis())
