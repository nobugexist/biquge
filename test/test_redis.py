import asyncio

from storage.aioredisclient import AioRedisClient
from storage.redisclient import RedisClient
from config.config import *


def test_redis():
    db = RedisClient()
    for i in range(1000):
        url = db.get_from_wait()
        print(url)



if __name__ == '__main__':
    test_redis()
