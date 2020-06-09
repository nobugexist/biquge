# redis数据库
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = None

# redis等待队列键值
REDIS_KEY_WAIT = "wait"
# 完成集合键值
REDIS_KEY_FINISH = "finish"

# mongo数据库配置
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB_NAME = "biquge"

# 直接存储的地址
DIRECT_STORAGE_MAIN_PATH = "/temp/biquge/"

# 并发数量
SPIDER_CONCURRENCY_NUM = 200

# url前缀地址
BASE_URL = "http://www.biquge.tv"

# 这个网站不校验header，也不封ip，用不上
DEFAULT_HEADERS = {

}

# 选择存储方式，选项为True时，以对应的方式存储
MONGO_SAVE = True
DIRECT_SAVE = False

