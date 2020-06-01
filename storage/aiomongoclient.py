import asyncio
import traceback

from loguru import logger as storage
from config.config import *
import motor.motor_asyncio


class AioMongoClient:
    def __init__(self, mongo_host=MONGO_HOST, mongo_port=MONGO_PORT):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_host, mongo_port)

    async def save_data(self, items, collection):
        db = self.client[MONGO_DB_NAME]
        try:
            # print(items)
            await db[collection].insert_one(items)
        except Exception:
            storage.error(f"Mongo insert failed{traceback.format_exc()},items now are {items}")


async def test_insert():
    for i in range(100000):
        await client.save_data({"s": i},"tests")
        print(i)


if __name__ == '__main__':
    # client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    # db_ = client.biquge_test
    client = AioMongoClient()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_insert())
