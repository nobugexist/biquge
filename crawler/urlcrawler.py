import traceback
import asyncio
import random
import sys
import traceback
import aiohttp
from loguru import logger as crawler
from config.config import *
from parse.parser import Parser
from storage.aiomongoclient import AioMongoClient
from storage.redisclient import RedisClient
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass
sys.path.append("..")


class UrlCrawler:
    def __init__(self, db=None, mongodb=None):
        self.db = db or RedisClient()
        self.mongodb = mongodb or AioMongoClient()

    async def get_child_urls(self, session, url):
        try:
            async with session.get(url, timeout=120) as resp:
                text = await resp.text()
                status_code = resp.status
                child_links, save_dict = Parser.parse_main_page(url, text)
                child_links = [url for url in child_links if self.db.check(url)]
                # print(child_links)
                self.db.multi_add_to_wait(child_links)
                await self.mongodb.save_data(save_dict, "book_list")
                await asyncio.sleep(random.random())
                crawler.info(f"get url: {url} status: {status_code}")
        except Exception:
            print(f"获取子链接出错：{traceback.format_exc()}")

    async def iter_urls(self):

        START_URL_LIST = ["https://www.biquge.tv/" + str(random.randint(0, 9)) + "_" + str(i) for i in range(1, 20001)]

        for i in range(0, len(START_URL_LIST), SPIDER_CONCURRENCY_NUM):
            session = aiohttp.ClientSession()
            urls = START_URL_LIST[i:i + SPIDER_CONCURRENCY_NUM]
            # print(urls)
            tasks = [asyncio.ensure_future(self.get_child_urls(session, url)) for url in urls]
            result = asyncio.wait(tasks)
            await result
            await asyncio.sleep(20)
            await session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    u = UrlCrawler()
    try:
        loop.run_until_complete(u.iter_urls())
    finally:
        loop.close()

"""
finalcount=24827551


"""
