import hashlib

import redis

from config.config import *


class RedisClient:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    # 检查是否重复
    def check(self, url):
        return not self.db.sismember(REDIS_KEY_FINISH, url)

    # 添加到finish集合中
    def add_to_finish(self, url):
        self.db.sadd(REDIS_KEY_FINISH, url)

    # 添加到wait队列中
    def add_to_wait(self, url):
        self.db.rpush(REDIS_KEY_WAIT, url)

    # 一次添加多个到wait队列中
    def multi_add_to_wait(self, urls):
        with self.db.pipeline(transaction=False) as p:
            for url in urls:
                self.db.rpush(REDIS_KEY_WAIT, url)
            p.execute()

    # 从wait队列中取一个
    def get_from_wait(self):
        return self.db.lpop(REDIS_KEY_WAIT)

    # 从wait队列中取多个
    def multi_get_from_wait(self, size):
        urls = self.db.lrange(REDIS_KEY_WAIT, 0, size)
        self.db.ltrim(REDIS_KEY_WAIT, size + 1, -1)
        return urls

    # 获取wait的数量
    def get_wait_count(self):
        return self.db.llen(REDIS_KEY_WAIT)

    # 对url进行MD5计算，转为16进制
    @staticmethod
    def hash_url(url):
        return hashlib.md5(bytes(url, encoding="utf-8")).hexdigest()
