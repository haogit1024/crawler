#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"a test py file"

import urllib

__author__ = 'chenzh'

import requests
import hashlib
import logging
import os
import time
import requests
# from util.HttpClient import WindowsChrome
from util.HttpClient import WindowsChrome

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

def fuck(i):
    time.sleep(2)
    print("wdnmd", i)


class Test(object):
    def fuck(self, i):
        print("aaaa", i)


def save_file(file_path: str, content: bytes):
    with open(file_path, 'wb') as f:
        f.write(content)


def get_file_content(file_path: str):
    with open(file_path, 'rb') as f:
        return f.read()


if __name__ == "__main__":
    # print('fuck python3')
    # save_file('test.cache', get_file_content(r'D:\code\test.jpg'))
    # save_file(r'.request_cache\f9751de431104b125f48dd79cc55822a', requests.get(r'https://www.baidu.com').content)
    # print(get_file_content(r'D:\cy_code\jenkinsfile').decode(encoding='UTF-8'))
    # create_time = os.path.getctime(r'D:\code\test.jpg')
    # print(create_time)
    # print(time.time())
    chrome = WindowsChrome()
    # chrome.del_cache()
    # chrome.download('https://introcs.cs.princeton.edu/java/data/leipzig/leipzig1m.txt', 'download/leipzig1m.txt', sync=True, referer='test111.com')
    # url = r'https://img.xchina.fun/photos/62c2fbea80afb/0001_600x0.jpg'
    # parse_result = urllib.parse.urlparse(url)
    # print(parse_result)
    # print(chrome.get_download_pool_amt())
    # print(urllib.parse.urlparse(url))
    # domain = parse_result.scheme + r'://' + parse_result.netloc
    # print(domain)
    # html = chrome.get("https://bundler.io/", "UTF-8")
    # print(html)
    chrome.download("https://bundler.io/application.min.js", "/Users/chenzhihao/work_space/domain/application.min.js")
    chrome.download("https://bundler.io/application.css", "/Users/chenzhihao/work_space/domain/application.css")
    chrome.download("https://bundler.io/images/header_transparent_bg@2x.png", "/Users/chenzhihao/work_space/domain/header_transparent_bg@2x.png")
    chrome.download("https://bundler.io/font/e68a5a6780c1d57a2eed.otf", "/Users/chenzhihao/work_space/domain/e68a5a6780c1d57a2eed.otf")
    chrome.download("https://bundler.io/manifest.json", "/Users/chenzhihao/work_space/domain/manifest.json")
    chrome.download("https://bundler.io/images/favicon-32x32.png", "/Users/chenzhihao/work_space/favicon-32x32.png")
    chrome.close(True)
    print("final")

