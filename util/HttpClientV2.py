from shutil import which
import requests
import logging
import os
import json
import time
from multiprocessing import Pool, Manager
import urllib.parse
from typing import Union


"""一个http客户端工具类, 主要是模拟浏览器的请求"""


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("HttpClientV2")


class BrowserMock(object):
    def __init__(
        self,
        enable_request_cache: bool = False,
        cache_path: str = "./.request_cache",
        cache_expire_second: int = 3600,
        download_tmp_dir: str = "./.download_tmp",
    ):
        """
        :param enable_download_cache: 是否开始请求缓存,如果开启将会缓存请求结果,再有效内直接返回缓存的数据
        :param request_cache_path: 缓存文件存放的路径
        :param request_cache_expire_second: 缓存过期秒数
        :param download_tmp_dir: 现在临时文件夹, 存放文件下载的信息，用户下载的暂停和继续
        """
        self.enable_request_cache = enable_request_cache
        self.cache_path = cache_path
        self.cache_expire_second = cache_expire_second
        self.download_tmp_dir = download_tmp_dir
        self.__session = requests.Session()
        # 单个进程锁
        m = Manager()
        self.__download_status_dict = m.dict()

    def get(self, url: str, encoding: str = "") -> Union[str, bytes]:
        """
        发送一个get请求
        :param url 请求连接
        :param encoding 编码
        :return 如果encoding === "" 则返回二进制内容,否者返回编码后的字符串
        """
        cache_content = None
        if self.enable_request_cache:
            cache_content = self.__get_request_cache_content(url)
            if cache_content is not None:
                log.info(f"从缓存中获取内容, url={url}")
                if encoding != "":
                    cache_content = cache_content.decode(encoding=encoding)
                return cache_content
        try:
            response = self.__session.get(url)
            if response.status_code == 200:
                if self.enable_request_cache:
                    self.__save_request_cache(url, response.content)
                if encoding != "":
                    return response.content.decode(encoding=encoding)
                else:
                    return response.content
            else:
                log.error(f"请求失败,status_code={response.status_code}, url={url}")
                return None
        except RuntimeError as e:
            log.error(f"get请求出错, url={url}")
            print(e)
            return ""

    def __get_request_cache_content(self, url: str) -> bytes:
        cache_file_path = self.__get_cache_content_path(url)
        if os.path.exists(cache_file_path):
            now = time.time()
            cache_create_time = os.path.getmtime(cache_file_path)
            if now - cache_create_time < self.cache_expire_second:
                with open(cache_file_path, "rb") as f:
                    return f.read()

    def __get_cache_content_path(self, url: str) -> str:
        """获取请求的缓存文件路径
        Args:
            url (str): 请求连接
        Returns:
            str: 缓存文件路径
        """
        return os.path.join(self.cache_path, urllib.parse.quote_plus(url))

    def __save_request_cache(self, url: str, content: bytes):
        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)
        cache_file_path = self.__get_cache_content_path(url)
        with open(cache_file_path, "wb") as f:
            f.write(content)

    def __get_download_cache_path(self, url: str) -> str:
        return os.path.join(self.download_tmp_dir, urllib.parse.quote_plus(url))

    def download(self, url: str, download_dir: str, file_name: str):
        cache_path = self.__get_download_cache_path(url)
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        save_path = os.path.join(download_dir, file_name)
        # 初始化下载信息
        download_info = {
            "http_url": url,  # 资源下载连接
            "save_path": save_path,  # 保存地址
            "index_byte": 0,  # 开始下载的字节索引
            "finish_time": 0,  # 下载完成时间
            "last_req_time": 0,  # 最后请求下载时间
            "length": 0,  # 文件总大小单位byte
            "mode": r"wb",  # python文件写入模式
            "fail_num": 0,
            "status": "begin",
        }
        self.__download(url, save_path, download_info, cache_path)

    def __download(
        self, url: str, save_path: str, download_info: dict, cache_path: str
    ):
        # 循环下载文件，如果需要终止下载，把download_info缓存到硬盘
        while True:
            # 判断是否下载完
            if (
                download_info["length"] != 0
                and download_info["index_byte"] >= download_info["length"]
            ):
                # 下载完成
                download_info["finish_time"] = int(time.time())
                download_info["status"] = "finish"
                self.__write_cache(cache_path, download_info)
                log.info("下载完成 " + url)
                return

    def __write_cache(self, cache_path: str, cache_data: dict):
        with open(cache_path, 'w') as f:
            f.write(json.dumps(cache_data))



if __name__ == "__main__":
    browser = BrowserMock(enable_request_cache=True)
    html = browser.get("https://www.baidu.com")
    print(html)
