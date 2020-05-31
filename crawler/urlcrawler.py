import json
import traceback
import asyncio
import random
from dataclasses import dataclass
import aiohttp
from loguru import logger as crawler
from lxml import html

from parse.parser import Parser
from storage.redisclient import RedisClient


class UrlCrawler:
    async def get_child_urls(self, session, db, url):
        try:
            async with session.get(url, timeout=120) as resp:
                if resp.status != 200:
                    db.add_to_wait(url)
                    return
                text = await resp.text()
                child_links, save_dict = Parser.parse_main_page(url, text)
                book_dict_list.append(save_dict)
                nodes = [str(url) for url in child_links]
                db.multi_add_to_wait(nodes)
                await asyncio.sleep(random.random())
                crawler.info(f"get url {url}")
        except Exception as e:
            print(traceback.format_exc())

    async def iter_urls(self):

        db = RedisClient()
        START_URL_LIST = ["https://www.biquge.tv/" + str(random.randint(0, 9)) + "_" + str(i) for i in range(1, 42392)]

        for i in range(0, len(START_URL_LIST), 200):
            session = aiohttp.ClientSession()
            urls = START_URL_LIST[i:i + 200]
            print(urls)
            tasks = [asyncio.ensure_future(self.get_child_urls(session, db, url)) for url in urls]
            result = asyncio.wait(tasks)
            await result
            await asyncio.sleep(0)
            await session.close()


if __name__ == '__main__':
    book_dict_list = list()
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    u = UrlCrawler()
    try:
        loop.run_until_complete(u.iter_urls())
    finally:
        loop.close()

    with open("../book_dict.json","w+",encoding="utf-8") as f:
        f.write(json.dumps(book_dict_list))

"""
finalcount=24827551


"""
