import asyncio

from crawler.urlcrawler import UrlCrawler

if __name__ == '__main__':
    U = UrlCrawler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(U.iter_urls())
    loop.close()