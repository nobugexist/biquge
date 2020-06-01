import asyncio
import sys
import threading

from config.config import *
from crawler.singlepagecrawler import SinglePageCrawler
from crawler.urlcrawler import UrlCrawler
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    new_loop = asyncio.get_event_loop()
    t = threading.Thread(target=start_loop, args=(new_loop,))
    t.start()

    if IS_MASTER:
        asyncio.run_coroutine_threadsafe(UrlCrawler().iter_urls(), new_loop)
    elif IS_SALVE:
        asyncio.run_coroutine_threadsafe(SinglePageCrawler().get_urls_to_crawl(), new_loop)
