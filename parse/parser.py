import re
import traceback
from loguru import logger as parser
from lxml import html


class Parser:
    @staticmethod
    def xpath(text, rule):
        root = html.fromstring(text)
        nodes = root.xpath(rule)
        return nodes

    @staticmethod
    def parse_main_page(url, text):
        book_name_r = '//*[@id="info"]/h1//text()'
        author_r = '//*[@id="info"]/p[1]//text()'
        last_update_r = '//*[@id="info"]/p[3]//text()'
        intro_r = '//*[@id="intro"]/p[1]//text()'
        child_links_r = '//*[@id="list"]/dl/dd/a//text()'

        save_dict = dict()
        child_links = ""
        try:
            child_links = Parser.xpath(text, child_links_r)
            book_id = url.split('/')[-1].split("_")[-1]
            save_dict["book_id"] = book_id
            save_dict["book_name"] = list(Parser.xpath(text, book_name_r))[0]
            save_dict["author"] = str(Parser.xpath(text, author_r)[0]).split("：")[-1]
            save_dict["last_update"] = str(Parser.xpath(text, last_update_r)[0]).split("：")[-1]
            save_dict["intro"] = Parser.xpath(text, intro_r)[0]
        except Exception:
            parser.error(f"Error error, here are details:{traceback.format_exc()}")

        return child_links, save_dict

    @staticmethod
    def parse_single_page(url, text):
        chapter_name_r = '//h1//text()'
        content_r = '//*[@id="content"]//text()'

        save_dict = dict()
        try:
            content = ''.join([str(i) for i in Parser.xpath(text, content_r)])
            # save_dict["chapter_name"] = list(Parser.xpath(text, chapter_name_r))[0]
            save_dict["chapter_name"] = re.sub(r"[/\\:*?\"<>|\s]", "_", list(Parser.xpath(text, chapter_name_r))[0])
            save_dict["content"] = content
            save_dict["url"] = url
            save_dict["text"] = text
        except Exception:
            parser.error(f"Error error, here are details:{traceback.format_exc()}")

        # print(save_dict)
        return save_dict
