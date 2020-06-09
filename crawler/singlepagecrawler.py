import asyncio
import traceback
from random import random
import aiohttp
from loguru import logger as crawler
from config.config import *
from parse.parser import Parser
from storage.aiomongoclient import AioMongoClient
from storage.directstorege import DirectStorage
from storage.redisclient import RedisClient

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class SinglePageCrawler:
    def __init__(self, db=None, mongodb=None):
        self.db = db or RedisClient()
        self.mongodb = mongodb or AioMongoClient()

    async def fetch_single_page_and_save_direct(self, session, url):
        """
        访问小说章节，并且直接存储
        :param session:
        :param url:
        :return:
        """
        async with session.get(url, timeout=15) as resp:
            try:
                status_code = resp.status
                # 失败重爬
                if status_code != 200:
                    self.db.add_to_wait(url)
                    return

                text = await resp.read()
                # xpath解析所需内容
                save_dict = Parser.parse_single_page(url, text)

                # 直接zlib压缩后存储
                await DirectStorage.save_single_page(url.split("/")[-2].split("_")[-1], save_dict["chapter_name"],
                                                     save_dict["content"])
                # url的16进制MD5添加到redis完成集合中
                self.db.add_to_finish(self.db.hash_url(url))

                crawler.info(f"get url: {url} status: {status_code}")
            except Exception:
                crawler.error(traceback.format_exc())
                self.db.add_to_wait(url)

    async def fetch_single_page_and_save_mongo(self, session, url):
        """
        访问小说章节，并且存储到mongodb中
        :param session:
        :param url:
        :return:
        """
        try:
            async with session.get(url, timeout=15) as resp:
                status_code = resp.status

                if status_code != 200:
                    self.db.add_to_wait(url)
                    return

                text = await resp.text("gbk", "ignore")
                save_dict = Parser.parse_single_page(url, text)

                await self.mongodb.save_data(save_dict, url.split("/")[-2].split("_")[-1])
                self.db.add_to_finish(self.db.hash_url(url))

                crawler.info(f"get url: {url} status: {status_code}")
        except Exception:
            crawler.error(traceback.format_exc())
            self.db.add_to_wait(url)

    async def get_urls_to_crawl(self):
        while True:
            try:
                session = aiohttp.ClientSession()
                # 全部url爬取完成后退出循环
                if self.db.get_wait_count() <= 0:
                    crawler.info("ALL URLS HAVE BEEN CRAWLED")
                    break
                # 从redis等待队列中
                urls = [BASE_URL + url for url in self.db.multi_get_from_wait(SPIDER_CONCURRENCY_NUM)]
                # 过滤已经访问过的页面
                urls = [url for url in urls if self.db.check(self.db.hash_url(url))]

                tasks = list()

                # 根据选项，执行不同的方法
                if MONGO_SAVE:
                    tasks = [asyncio.ensure_future(self.fetch_single_page_and_save_mongo(session, url)) for url in urls]
                elif DIRECT_SAVE:
                    tasks = [asyncio.ensure_future(self.fetch_single_page_and_save_direct(session, url)) for url in urls]

                result = asyncio.wait(tasks)
                await result

                await session.close()
                await asyncio.sleep(3)

            except Exception:
                crawler.error(traceback.format_exc())


def test_crawler():
    C = SinglePageCrawler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(C.get_urls_to_crawl())


if __name__ == '__main__':
    # db = RedisClient()
    # urls = db.multi_get_from_wait(100)
    # print(urls)
    test_crawler()
