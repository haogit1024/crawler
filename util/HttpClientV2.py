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
            "download_size": 0,  # 第一次下载大小，单位KB
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
            # 没下载完
            # 组装请求头 计算range 和 referer
            start_byte = download_info['index_byte']
            download_size = download_info['download_size']
            referer = download_size['referer']
            if referer is None:
                parse_result = urllib.parse.urlparse(url)
                referer = parse_result.scheme + r'://' + parse_result.netloc + r'/'
            end_byte = start_byte + download_size * 1024
            range = 'bytes={start}-{end}'.format(start=start_byte, end=end_byte)
            headers: dict = self.__gen_download_header(referer, range)
            # 请求内容，并计算下载时间和调整每次下载大小
            now_time = time.time()
            try:
                # 下载单位 1 秒
                req_time_unin = 1000
                req_start_time = int(round(now_time * 1000))
                response = self.__session.get(url, headers=headers, timeout=(100, 100))
                # todo 判断没有返回 Content-Range，即不用断点下载的场景
                req_end_time = int(round(time.time() * 1000))
                used_time = req_end_time - req_start_time
                response_content_range = response.headers['Content-Range']
                file_length, rel_start_byte, rel_end_byte = self.__parse_content_range(response_content_range)
                download_rate = (rel_end_byte / file_length) * 100
                download_info['length'] = file_length
                log.info(f'{url}, download_size: {download_size}, save_path: {save_path}')
                log.info(f'{url}, download_use_time: {used_time}')
                # 下载速度
                download_speed = int(((rel_end_byte - rel_start_byte) / 1024) / (used_time / 1000))
                # download_speed = 0 处理
                if download_speed == 0:
                    log.error('download_speed为0')
                    log.error('rel_end_byte:' + str(rel_end_byte))
                    log.error('rel_start_byte:' + str(rel_start_byte))
                    log.error('use_time:' + str(used_time))
                    download_speed = 100
                # 剩余下载时间(单位秒)
                download_remaining_time = int((file_length - rel_end_byte) / 1024 / download_speed)
                log.info(f'{url}, download_speed: {download_speed} k/s')
                log.info(f'{url}, download_rate: {download_rate} %')
                log.info(f'{url}, download_remaining_time: {download_remaining_time} second')
                if used_time < req_time_unin:
                    # 提速
                    speed = req_time_unin / used_time
                    download_size = int(download_size * speed)
                elif used_time > req_time_unin:
                    # 降速
                    speed = used_time / req_time_unin
                    download_size = int(download_size / speed)
                # 这里有个bug，如果有一次download_size = 0 就永远就下载不了文件了
                if download_size == 0:
                    log.info(f'{url}, 下载速度为0, 重新调整下载速度')
                    download_size = 5
                # todo status code 不是 206 处理

                # 写入文件
                with open(save_path, download_info['mode']) as f:
                    f.write(response.content)
                    download_info['mode'] = 'ab'
                # 更新download_info并缓存
                download_info['index_byte'] = end_byte + 1
                download_info['last_req_time'] = int(now_time)
                download_info['status'] = 'running'
                self.__write_cache(cache_path, download_info)
            except Exception as e:
                log.exception(e)
                log.error(f"下载出错, url={url}")

    def __gen_download_header(self, referer: str, range: str) -> dict:
        return {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            # 'Upgrade-Insecure-Requests': '1',
            'referer': referer,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Microsoft Edge";v="98"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'image',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'cross-site',
            'Range': range,
        }

    def __parse_content_range(self, content_range: str) -> tuple:
        """
        解析http的Content-Range响应头
        :param content_range: bytes 0-10/1560323
        :return: file_length, start_byte, end_byte
        """
        content_arr = content_range.split(r'/')
        file_length = int(content_arr[1])
        bytes_arr = content_arr[0].split(r' ')
        index_arr = bytes_arr[1].split(r'-')
        return int(file_length), int(index_arr[0]), int(index_arr[1])

    def __write_cache(self, cache_path: str, cache_data: dict):
        with open(cache_path, 'w') as f:
            f.write(json.dumps(cache_data))


if __name__ == "__main__":
    browser = BrowserMock(enable_request_cache=True)
    html = browser.get("https://www.baidu.com")
    print(html)
