# !/usr/bin/python
# -*- coding: utf-8 -*-


import asyncio
import aiohttp
from cchardet import detect
from lxml import etree
import json


result = []
loop = asyncio.get_event_loop()


class HighRequest():
    def __init__(self, method, url, timeout=None, session=False, headers=None, cookies=None, unsafe=None,
                 mark='xqq', **kwargs):
        self.method, self.session, self.url, self.mark, self.timeout = method, session, url, mark, timeout
        callback = kwargs.pop('callback', None)
        self.callback = callback
        self.kwargs = kwargs
        if not session:
            self.sessiondict = (cookies, headers, aiohttp.CookieJar(unsafe=True) if unsafe else None)


async def main(url, method, timeout=None, headers=None, cookies=None, proxy=None, data=None, params=None):
    async with aiohttp.ClientSession() as client:
        try:
            async with client.request(url=url, method=method, headers=headers, timeout=timeout, cookies=cookies,
                                      proxy=proxy, data=data, params=params) as resp:
                result.append(HighResponse(await resp.read(), resp))
        except:
            pass


def request(url, method, timeout=None, headers=None, cookies=None, proxy=None, data=None, params=None):
    loop.run_until_complete(main(url, method, timeout, headers, cookies, proxy, data, params))
    return result


def requests(urls, method, timeout=None, headers=None, cookies=None, proxy=None, data=None, params=None):
    tasks = []
    for url in urls:
        tasks.append(asyncio.ensure_future(main(url, method, timeout, headers, cookies, proxy, data, params)))
    loop.run_until_complete(asyncio.wait(tasks))
    return result


def get(url, timeout=60, headers=None, cookies=None, proxy=None, data=None):
    request(url, 'GET', timeout, headers, cookies, proxy, data=None, params=data)
    return result[0]


def post(url, timeout=60, headers=None, cookies=None, proxy=None, data=None):
    request(url, 'POST', timeout, headers, cookies, proxy, data=data, params=None)
    return result[0]


def gets(urls, timeout=60, headers=None, cookies=None, proxy=None, data=None):
    requests(urls, 'GET', timeout, headers, cookies, proxy, data=None, params=data)
    return result


class HighResponse():
    def __init__(self, content, clientResponse):
        self.content = content
        self.clientResponse = clientResponse

    def raw(self):
        return self.clientResponse

    @property
    def url(self):
        return self.clientResponse.url

    @property
    def cookies(self):
        return self.clientResponse.cookies

    @property
    def headers(self):
        return self.clientResponse.headers

    @property
    def status(self):
        return self.clientResponse.status

    @property
    def method(self):
        return self.clientResponse.method

    @property
    def text(self, encoding=None):
        encoding = encoding or detect(self.content)['encoding']
        return self.content.decode(encoding=encoding)

    def get_element_for_xpath(self, str):
        return etree.HTML(self.content).xpath(str)[0]

    def get_elements_for_xpath(self, str):
        return etree.HTML(self.content).xpath(str)

    @property
    def json(self):
        return json.loads(self.text)

    def get_value_from_key(self, key):
        json_results = []
        return get_value_by_key(self.json, json_results, key)[0]

    def get_values_from_key(self, key):
        json_results = []
        return get_value_by_key(self.json, json_results, key)

    def __repr__(self):
        return "<HighResponse [status {}]>".format(self.clientResponse.status)

    __str__ = __repr__


def get_dict_from_str(param):
    params = {}
    for data in param.split('\n'):
        params.update({data.split(':')[0].strip(): data.split(':')[1].strip()})
    return params


def get_value_by_key(input_json, results, key):
    key_value = ''
    if isinstance(input_json, dict):
        for json_result in input_json.values():
            if key in input_json.keys():
                key_value = input_json.get(key)
            else:
                get_value_by_key(json_result, results, key)
    elif isinstance(input_json, list):
        for json_array in input_json:
            get_value_by_key(json_array, results, key)
    if key_value != '':
        results.append(key_value)
    return results
