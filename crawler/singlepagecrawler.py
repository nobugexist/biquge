import asyncio
import os
import time
import traceback
from dataclasses import dataclass
from random import random, randint
import re
from loguru import logger as crawler
import aiohttp

from parse.parser import Parser
from storage.directstorege import DirectStorage
from storage.redisclient import RedisClient
from config.config import *


class SinglePageCrawler:
    def __init__(self, db=None):
        self.db = db or RedisClient()


    async def fetch_single_page_and_save_direct(self,session, url):
        async with session.get(url, timeout=30) as resp:
            try:
                if resp.status != 200:
                    self.db.add_to_wait(url)
                    return
                text = await resp.read()
                save_dict = Parser.parse_single_page(url, text)
                book_name = url.split("/")[-2].split("_")[-1]
                # print(save_dict)
                # 维护一个json格式的字典，找到每本书的的url对应的书名
                await DirectStorage.save_single_page(book_name, save_dict["chapter_name"], save_dict["content"])
                # await DirectStorage.save_single_page("1", str(randint(1,100000)), text)
                crawler.info(f"get url {url}")
            except IndexError as e:
                crawler.error(traceback.format_exc())


    async def fetch_single_page_and_save_mongo(self,session, url):
        async with session.get(url, timeout=15) as resp:
            text = await resp.text()
            save_dict = Parser.parse_single_page(url, text)

    async def get_urls_to_crawl(self):


        # while True:
        for i in range(25):
            session = aiohttp.ClientSession()
            if self.db.get_wait_count() <= 0:
                crawler.info("ALL URLS HAVE BEEN CRAWLED")
                break

            urls = [BASE_URL + url for url in self.db.multi_get_from_wait(SPIDER_CONCURRENCY_NUM)]
            tasks = list()

            if MONGO_SAVE:
                tasks = [asyncio.create_task(self.fetch_single_page_and_save_mongo(session, url)) for url in urls]
            elif DIRECT_SAVE:
                tasks = [asyncio.create_task(self.fetch_single_page_and_save_direct(session, url)) for url in urls]

            result = asyncio.gather(*tasks)
            await result
            await session.close()


def test_crawler():
    crawler = SinglePageCrawler()
    asyncio.run(crawler.get_urls_to_crawl())


if __name__ == '__main__':
    s = time.time()
    test_crawler()
    e =time.time()
    print(e - s)
