import asyncio
import os
import zlib

import aiofiles
from loguru import logger as storage

from config.config import *


class DirectStorage:

    @staticmethod
    async def save_single_page(book_name, file_name, text):
        """
        直接文件形式存储小说章节
        :param book_name: 书名
        :param file_name: 章节名
        :param text: 章节内容
        :return:
        """
        # 进行文件夹判断，创建
        file_dir = os.path.join(DIRECT_STORAGE_MAIN_PATH, book_name)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        full_filepath = os.path.join(file_dir, file_name)

        # zlib压缩，节省磁盘空间
        text = zlib.compress(bytes(text.encode("utf-8")), 5)
        # aiofiles异步写入文件，加快速度
        async with aiofiles.open(full_filepath, "wb+") as f:
            await f.write(text)

        storage.info(f"successfully saved binary {file_name} ")


def test():
    asyncio.run(DirectStorage.save_single_page("21", "ddas.txt", "dasdas312dadasdas"))


if __name__ == '__main__':
    test()
