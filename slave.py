import asyncio

from crawler.singlepagecrawler import SinglePageCrawler

if __name__ == '__main__':
    V = SinglePageCrawler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(V.get_urls_to_crawl())
    loop.close()