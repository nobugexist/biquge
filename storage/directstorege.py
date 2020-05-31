import asyncio
import os
import aiofiles
from loguru import logger as storage
from config.config import *
import zlib


class DirectStorage:

    @staticmethod
    async def save_single_page(book_name, file_name, text):
        file_dir = os.path.join(DIRECT_STORAGE_MAIN_PATH, book_name)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        # print(file_dir,file_name)
        full_filepath = os.path.join(file_dir, file_name)
        # print(len(text))
        text = zlib.compress(bytes(text.encode("utf-8")), 5)
        # print(len(text))
        async with aiofiles.open(full_filepath, "wb+") as f:
            await f.write(text)

        storage.info(f"successfully saved binary {file_name} ")


def test():
    asyncio.run(DirectStorage.save_single_page("21", "ddas.txt", "dasdas312dadasdas"))


if __name__ == '__main__':
    test()
