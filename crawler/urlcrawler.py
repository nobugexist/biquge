import asyncio
import random
import traceback
import aiohttp
from loguru import logger as crawler
from config.config import *
from parse.parser import Parser
from storage.aiomongoclient import AioMongoClient
from storage.redisclient import RedisClient

# uvloop可以使asyncio更快，但是目前是由linux下的实现
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class UrlCrawler:
    def __init__(self, db=None, mongodb=None):
        self.db = db or RedisClient()
        self.mongodb = mongodb or AioMongoClient()

    async def get_child_urls(self, session, url):
        """
        获取小说章节目录页中所包含的所有子链接
        :param session:
        :param url:
        :return:
        """
        try:
            async with session.get(url, timeout=120) as resp:
                text = await resp.text("gbk", "ignore")
                status_code = resp.status

                # xpath解析出子url
                child_links, save_dict = Parser.parse_main_page(url, text)
                child_links = list(set(child_links))

                # 将子链接添加到redis等待队列中
                self.db.multi_add_to_wait(child_links)
                # 存储到mongodb中
                await self.mongodb.save_data(save_dict, "book_list")

                crawler.info(f"get url: {url} status: {status_code}")
        except Exception:
            crawler.error(f"获取子链接出错：{traceback.format_exc()}")

    async def iter_urls(self):
        """
        分批次，根据并发数量访问所有小说的章节目录页
        :return:
        """
        # 拼接url
        START_URL_LIST = [BASE_URL + "/" + str(random.randint(0, 9)) + "_" + str(i) for i in range(1, 42000)]

        for i in range(0, len(START_URL_LIST), SPIDER_CONCURRENCY_NUM):
            session = aiohttp.ClientSession()
            urls = START_URL_LIST[i:i + SPIDER_CONCURRENCY_NUM]

            # 多协程的灵魂
            tasks = [asyncio.ensure_future(self.get_child_urls(session, url)) for url in urls]
            result = asyncio.wait(tasks)

            await result
            await session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    u = UrlCrawler()
    try:
        loop.run_until_complete(u.iter_urls())
    finally:
        loop.close()
