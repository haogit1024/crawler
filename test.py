#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""a test py file"""

__author__ = 'chenzh'

import logging
import os
import sys
import time
from util.HttpClient import WindowsChrome

import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("WindowsChrome")


def fuck():
    # 2177128
    headers = {
        "Range": r"bytes=0-1177128"
    }
    # response = requests.get("http://www.hywdyy.top/test/test.zip")
    response = requests.get("http://www.hywdyy.top/test/test.jpg", headers=headers)
    with open(r"C:\Users\admin\Desktop\test\test.jpg", "wb") as f:
        f.write(response.content)
    print(response.status_code)
    print(response.headers)
    headers = {
        "Range": r"bytes=1177129-2177127"
    }
    response = requests.get("http://www.hywdyy.top/test/test.jpg", headers=headers)
    with open(r"C:\Users\admin\Desktop\test\test.jpg", "ab") as f:
        f.write(response.content)
    return response


def hello():
    yield 1
    yield 2

class Test(object):
    def fuck(self, i):
        print("aaaa", i)


def save_file(file_path: str, content: bytes):
    with open(file_path, 'wb') as f:
        f.write(content)


def get_file_content(file_path: str) -> bytes:
    with open(file_path, 'rb') as f:
        return f.read()


def foo(*args, **kw):
    print('args', args)
    print('kw', kw)


if __name__ == "__main__":
    # img_url = r'http://up.keaitupian.com//uploads/imgs/2018/1006/df0c3aef566d75d9740efee10b654130.jpg'
    # download_path = r'D:\spider_file\liufeier\test.jpg'
    chrome = WindowsChrome(max_download_num=24, enable_request_cache=True, request_cache_effective_time=1800)
    # chrome.download(img_url, download_path, download_size=100, sync=True)
    # chrome.close(True)
    # chrome.del_cache()
    # print("test")
    # print(os.stat(r'/Users/chenzhihao/spider_data/grand_blue/单话/第11回/21.jpg').st_size)
    # js = chrome.get(r'https://www.maofly.com/static/js/preload.jquery.js', 'UTF-8')
    # print(js)
    html = chrome.get('https://meituan.com/', 'UTF-8')
    print(html)
    chrome.close(True)

