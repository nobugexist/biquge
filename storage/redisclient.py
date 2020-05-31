import hashlib

import redis

from config.config import *


class RedisClient:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def check(self, url):
        return not self.db.sismember(REDIS_KEY_FINISH, url)

    def add_to_finish(self, url):
        self.db.sadd(REDIS_KEY_FINISH, url)

    def add_to_wait(self, url):
        self.db.rpush(REDIS_KEY_WAIT, url)

    def multi_add_to_wait(self, urls):
        with self.db.pipeline(transaction=False) as p:
            for url in urls:
                self.db.rpush(REDIS_KEY_WAIT, url)
            p.execute()

    def get_from_wait(self):
        return self.db.lpop(REDIS_KEY_WAIT)

    def multi_get_from_wait(self,size):
        urls = self.db.lrange(REDIS_KEY_WAIT, 0, size)
        self.db.ltrim(REDIS_KEY_WAIT, size + 1, -1)
        return urls

    def get_wait_count(self):
        return self.db.llen(REDIS_KEY_WAIT)

    def get_finish_count(self):
        return self.db.scard(REDIS_KEY_FINISH)

    @staticmethod
    def hash_url(url):
        return hashlib.md5(bytes(url, encoding="utf-8")).hexdigest()
