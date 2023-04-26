import requests
import logging
import os
import json
import time
import hashlib
from abc import ABCMeta, abstractmethod
from multiprocessing import Pool, Process, Manager
import shutil
import urllib

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("WindowsChrome")


class BaseHttpClient(object, metaclass=ABCMeta):
    @abstractmethod
    def get(self, url, encoding=None):
        pass

    @abstractmethod
    def post(self, url, data, encoding=None):
        pass

    @abstractmethod
    def download(self, http_url, save_path, alias=None):
        pass


class DownloadUtil(object):
    """
    去他妈的python的processes模块和pickled模块不支持序列化当前对象和lambda，所以新建一个类做并发下载
    """

    def __init__(self, download_cache_path: str = r'.download_cache', enable_cache=True, cache_effective_time=1800):
        """
        初始化下载工具
        :param download_cache_path:     下载路径
        :param enable_cache:            是否开启缓存, 开启下载缓存会加大硬盘空间占用
        :param cache_effective_time:    缓存有效时间
        """
        self.download_cache_path = download_cache_path
        self.download_cache_file_path = os.path.join(download_cache_path, "file")
        self.enable_cache = enable_cache
        self.cache_effective_time = cache_effective_time
        m = Manager()
        self.__download_status_dict = m.dict()
        requests.DEFAULT_RETRIES = 1
        self.__session = requests.session()
        self.__session.keep_alive = True
        self.__session.max_redirects = 1
        # proxies = {
        #     "http": "http://localhost:1082",
        #     "https": "http://localhost:1082",
        # }
        # self.proxies = proxies
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            # 'Upgrade-Insecure-Requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'accept': 'gzip, deflate, br',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'image',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'cross-site'
        }
        self.cookie = None

    def download(self, http_url: str, save_path: str, download_size=10, referer=None):
        try:
            # 创建缓存文件夹
            cache_name = self.__md5(save_path)
            log.info("download file, " + cache_name)
            cache_file_path = self.__create_cache_file(http_url, cache_name, save_path, referer)
            # 获取缓存
            cache_path = self.__get_download_cache(cache_name)
            log.info("cache_name: " + cache_name)
            log.info("cache_path: " + str(cache_path))
            if cache_path is not None:
                log.info('下载文件命中缓存, http_url: ' + http_url)
                shutil.copy(cache_path, save_path)
                return
            self.__download_status_dict[cache_file_path] = True
            self.__download_file(cache_file_path, download_size)
            self.__create_download_cache(save_path, cache_name)
        except Exception as e:
            print(e)
            log.exception(e)
            log.error(str(e))
            log.error(repr(e))
            log.error("创建下载任务出错, url: " + http_url)

    def download_and_alias(self, http_url: str, save_path, alias=None, download_size=10):
        final_save_path = os.path.join(save_path, alias)
        return self.download(http_url, final_save_path, download_size)

    def contains_download(self, cache_name: str = None, cache_path: str = None):
        """
        继续下载单个文件
        :param cache_name: 缓存文件名
        :param cache_path: 缓存文件路径
        :return:
        """
        if cache_name is None and cache_path is None:
            log.error("cache_name and cache_path不能同时为空")
            return
        if cache_name is not None:
            rel_cache_path = os.path.join(self.download_cache_path, cache_name)
        else:
            rel_cache_path = cache_path
        self.__download_file(rel_cache_path, is_continue=True)

    def __download_file(self, cache_path: str, download_size: int = 10, is_continue=False):
        """
        下载文件方法，每次只下载一部分，递归执行，可以计算网络速度
        :param cache_path: 缓存文件路径
        :param download_size: 这次下载速度
        :param is_continue: 是否断开后重新下载
        :return: None
        """
        cache_data = self.__read_cache(cache_path)
        http_url = cache_data['http_url']
        save_path = cache_data['save_path']
        start_byte = cache_data['index_byte']
        referer = cache_data['referer']

        # 如果是重新下载，start_byte应该根据文件大小来算
        if is_continue:
            already_download_size = os.path.getsize(save_path)
            start_byte = already_download_size

        # 判断是否下载完成
        if cache_data['length'] != 0 and cache_data['index_byte'] >= cache_data['length']:
            # 下载完成
            cache_data['finish_time'] = int(time.time())
            cache_data['status'] = 'finish'
            self.__write_cache(cache_path, cache_data)
            log.info("下载完成 " + http_url)
            return

        if self.__download_status_dict.get(cache_path) is None:
            self.__download_status_dict[cache_path] = True
        if not self.__download_status_dict[cache_path]:
            log.info("手动停止下载")
            return

        # 一次下载{download_size}k
        end_byte = start_byte + download_size * 1024
        range = 'bytes={start}-{end}'.format(start=start_byte, end=end_byte)
        log.info("Request Range: " + range)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            # 'Upgrade-Insecure-Requests': '1',
            'referer': referer,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Microsoft Edge";v="98"',
            'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"macOS"', 'sec-fetch-dest': 'image',
            'sec-fetch-mode': 'no-cors', 'sec-fetch-site': 'cross-site', 'Range': range}
        # headers = {"Range": range}
        now_time = time.time()
        try:
            # 设置每次下载耗时接近1秒
            req_time_util = 1000
            req_start_time = int(round(now_time * 1000))
            try:
                response = self.__session.get(http_url, headers=headers, timeout=(100, 100))
                # response = requests.get(http_url, headers=headers)
            except Exception as e:
                print(e)
                log.error(str(e))
                log.error(repr(e))
                log.error("下载出错, url: " + http_url)
                cache_data['fail_num'] = cache_data['fail_num'] + 1
                cache_data['status'] = 'fail'
                cache_data['error_msg'] = repr(e)
                self.__write_cache(cache_path, cache_data)
                return
            if not response.headers.__contains__('Content-Range'):
                log.info('header not contains Content-Range, response headers: ')
                log.info(response.headers)
                log.info(len(response.content))
                log.info(cache_data['http_url'])
                log.info('cache_path:' + cache_path)
                os.remove(cache_path)
                log.info('删除缓存文件成功')
                log.info(response.status_code)
                log.info(response.content)
                # 没有content-range响应头，直接写入数据
                # with open(save_path, cache_data['mode']) as f:
                #     f.write(response.content)
                return
            # 计算下载需要的时间，适当提高下载速度。目前以2秒为一个下载区间
            req_end_time = int(round(time.time() * 1000))
            use_time = req_end_time - req_start_time
            # 如果下载的内容很小, 响应时间可能会等于0
            # 根据响应头计算download_size
            #                         bytes 0-10/1560323
            response_content_range = response.headers['Content-Range']
            log.info("Response Content-Range: " + response_content_range)
            file_length, rel_start_byte, rel_end_byte = self.__parse_content_range(response_content_range)
            #                           bytes 13412480-13412480/21390448
            # 获取下载百分比
            download_rate = (rel_end_byte / file_length) * 100
            cache_data['length'] = file_length
            log.info(http_url + ", download_size: " + str(download_size) + ', save_path: ' + save_path)
            log.info(http_url + ", download_use_time: " + str(use_time))
            # 下载速度
            download_speed = int(((rel_end_byte - rel_start_byte) / 1024) / (use_time / 1000))
            # download_speed = 0 处理
            if download_speed == 0:
                log.error('download_speed为0')
                log.error('rel_end_byte:' + str(rel_end_byte))
                log.error('rel_start_byte:' + str(rel_start_byte))
                log.error('use_time:' + str(use_time))
                download_speed = 100
            # 剩余下载时间(单位秒)
            download_remaining_time = int((file_length - rel_end_byte) / 1024 / download_speed)
            log.info("%s, download_speed: %d k/s" % (http_url, download_speed))
            log.info("%s, download_rate: %.2f %%" % (http_url, download_rate))
            log.info("%s, download_remaining_time: %d second" % (http_url, download_remaining_time))
            if use_time < req_time_util:
                # 提速
                speed = req_time_util / use_time
                download_size = int(download_size * speed)
            elif use_time > req_time_util:
                # 降速
                speed = use_time / req_time_util
                download_size = int(download_size / speed)
            # 这里有个bug，如果有一次download_size = 0 就永远就下载不了文件了
            if download_size == 0:
                log.info('%s, 下载速度为0, 重新调整下载速度' % http_url)
                download_size = 5
        except Exception as e:
            logging.exception(e)
            log.error('下载错误' + http_url)
            return

        if response.status_code != 206:
            log.error('下载错误, url: %s, status_code: %d' % (http_url, response.status_code))
            return

        # 写入文件
        with open(save_path, cache_data['mode']) as f:
            f.write(response.content)
            # 下载完一部分后修改文件写入状态
            cache_data['mode'] = r'ab'
        # 更新缓存文件
        cache_data['index_byte'] = end_byte + 1
        cache_data['last_req_time'] = int(now_time)
        cache_data['status'] = 'running'
        self.__write_cache(cache_path, cache_data)
        self.__download_file(cache_path, download_size)

    def stop_download(self, cache_file_name: str = None, cache_path: str = None):
        if cache_path is None and cache_file_name is None:
            log.error("停止下载文件出错")
            return
        if cache_path is None:
            cache_path = os.path.join(self.download_cache_path, cache_file_name)
        self.__download_status_dict[cache_path] = False

    def display_dict(self):
        log.info(r"cache_dict", self.__download_status_dict)

    def list_cache_file(self):
        """
        返回所有缓存文件
        :return: list[file]
        """
        pass

    def __create_cache_file(self, http_url: str, cache_name: str, save_path: str, referer: str = None) -> str:
        """
        创建缓存文件，并返回缓存文件路径
        :param http_url
        :param cache_name:
        :param save_path:
        :return:
        """
        if not os.path.exists(self.download_cache_path):
            os.makedirs(self.download_cache_path)
        # 根据save_path创建文件夹
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        #           /xxx.xx            xxx.xx
        cache_file_path = os.path.join(self.download_cache_path, cache_name)
        parse_result = urllib.parse.urlparse(http_url)
        if referer is None:
            referer = parse_result.scheme + r'://' + parse_result.netloc + r'/'
        with open(cache_file_path, 'w') as f:
            cache_data = {
                'http_url': http_url,  # 资源下载连接
                'save_path': save_path,  # 保存地址
                "index_byte": 0,  # 开始下载的字节索引
                "finish_time": 0,  # 下载完成时间
                "last_req_time": 0,  # 最后请求下载时间
                "length": 0,  # 文件总大小单位byte
                "mode": r"wb",  # python文件写入模式
                "fail_num": 0,
                "status": "begin",
                "referer": referer
            }
            f.write(json.dumps(cache_data))
        return cache_file_path

    def __read_cache(self, cache_path: str) -> dict:
        """
        读取缓存文件
        :param cache_path: 缓存文件路径
        :return: dict 配置文件
        """
        with open(cache_path, 'r') as f:
            return json.load(f)

    def __write_cache(self, cache_path: str, cache_data: dict):
        """
        写入配置文件
        :param cache_path: 缓存文件路径
        :param cache_data: 配置字典
        :return: None
        """
        with open(cache_path, 'w') as f:
            f.write(json.dumps(cache_data))

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

    def __md5(self, content: str):
        md5 = hashlib.md5()
        md5.update(content.encode(r"utf-8"))
        return md5.hexdigest()

    def __get_download_cache(self, cache_name: str) -> str:
        """
        如何缓存生效且缓存在有效期内，返回缓存文件路径
        :param cache_name:
        :return:
        """
        cache_file = os.path.join(self.download_cache_file_path, cache_name)
        if self.enable_cache and os.path.exists(cache_file):
            create_time = os.path.getmtime(cache_file)
            now = time.time()
            # log.info('----------')
            # log.info(create_time)
            # log.info(now)
            # log.info(self.cache_effective_time)
            # log.info('----------')
            if now - create_time < self.cache_effective_time:
                return cache_file

    def __create_download_cache(self, download_file_path: str, cache_name: str):
        """
        创建下载文件
        :param download_file_path: 下载完成后的文件名
        :param cache_name:         生成的缓存文件名
        :return:
        """
        if not os.path.exists(self.download_cache_file_path):
            os.mkdir(self.download_cache_file_path)
        if os.path.exists(download_file_path):
            cache_file_path = os.path.join(self.download_cache_file_path, cache_name)
            # if cache_file_path =
            shutil.copy(download_file_path, cache_file_path)
            log.info('创建下载文件缓存, cache_name: ' + cache_name)

    def del_cache(self):
        delete_cache(self.download_cache_path, self.cache_effective_time)
        delete_cache(self.download_cache_file_path, self.cache_effective_time)


class WindowsChrome(BaseHttpClient):
    def __init__(self, max_download_num: int = None, download_cache_path: str = r'.download_cache',
                 enable_request_cache: bool = False, request_cache_path: str = r'.request_cache',
                 request_cache_effective_time: int = 3600):
        """
        初始化浏览器 TODO 整合 download_cache_path 和 request_cache_path
        :param max_download_num: 最大下载进程数
        :param download_cache_path: 断点续传缓存文件
        :param enable_request_cache: 是否开启请求缓存
        :param request_cache_path: 请求缓存文件路径
        :param request_cache_effective_time: 请求缓存有效时间，单位秒
        """
        self.session = None
        download_num = max_download_num
        if download_num is None:
            download_num = os.cpu_count() * 2
            if download_num < 10:
                download_num = 10
        self.__download_pool = Pool(processes=download_num)
        self.__download_status_dict = {}
        self.download_cache_path = download_cache_path
        self.download_util = DownloadUtil(download_cache_path, enable_request_cache, request_cache_effective_time)
        self.enable_request_cache = enable_request_cache
        self.request_cache_path = request_cache_path
        self.request_cache_effective_time = request_cache_effective_time
        # proxies = {
        #     "http": "http://127.0.0.1:1082",
        #     "https": "http://127.0.0.1:1082",
        # }
        # self.proxies = proxies

    def init_session(self, url: str):
        requests.get(url, headers=self.headers)
        self.session = requests.session()

    def get(self, url: str, encoding: str = None):
        """
        获取http请求response
        :param url: 请求url
        :param encoding: encoding:需要解析成指定的字符编码
        :return:
        """
        cache_content = None
        # 读取缓存文件
        if self.enable_request_cache:
            cache_content = self.__get_cache(url)
            if cache_content is not None:
                if encoding is not None:
                    cache_content = cache_content.decode(encoding=encoding)
                return cache_content
        try:
            if self.session is None:
                log.info("WindowsChrome requesting...")
                response = requests.get(url)
                log.info("WindowsChrome request finish...")
            else:
                log.info("WindowsChrome session requesting...")
                response = self.session.get(url)
                log.info("WindowsChrome session request finish...")
            if response.status_code == 200:
                if self.enable_request_cache and cache_content is None:
                    self.__save_cache(url, response.content)
                    # self.__save_cache(url, bytes(r'just say WDNMD', encoding='UTF-8'))
                if encoding is not None:
                    # log.info('return encoding string')
                    return response.content.decode(encoding=encoding)
                else:
                    # log.info('return binary object')
                    return response.content
            else:
                log.error('访问url失败')
                log.info('url=%s, statusCode=%s' % (url, response.status_code))
                return None
        except RuntimeError as e:
            log.error('http访问出错,url=%s' % url)
            print(e)

    def post(self, url: str, data: dict, encoding=None):
        pass

    def __get_cache(self, url: str) -> bytes:
        cache_file = os.path.join(self.request_cache_path, md5(url))

        if os.path.exists(cache_file):
            now = time.time()
            cache_create_time = os.path.getmtime(cache_file)
            # log.info("now %s, cache_create_time %s, diff %s", str(now), str(cache_create_time), str(now - cache_create_time))
            if now - cache_create_time < self.request_cache_effective_time:
                with open(cache_file, 'rb') as f:
                    log.info('开始读取缓存文件, url：' + url + ", cache_file: " + cache_file)
                    return f.read()

    def __save_cache(self, url: str, content: bytes):
        # 创建缓存文件夹
        if not os.path.exists(self.request_cache_path):
            os.makedirs(self.request_cache_path)
        cache_file = os.path.join(self.request_cache_path, md5(url))
        with open(cache_file, 'wb') as f:
            log.info('开始写入缓存文件, url：' + url + ", cache_file: " + cache_file)
            f.write(content)

    def get_download_pool_amt(self):
        return len(self.__download_pool._cache)

    def download(self, http_url: str, save_path: str, alias=None, download_size=10, sync=False, referer=None):
        """
        :source_url: 下载文件的url
        :save_path: 文件保存路径
        :alias: 文件别称
        :sync: 是否是开启异步下载, 利用进程池实现, 为True时, 用户必须要等进程池的进程都执行完之后才能结束主(用户)进程,
        调用 close(True)方法可以达到效果
        """
        if sync:
            log.info("异步下载")
            # 获取进程池和往进程池添加一个task
            # p = Process(target=self.download_util.download, args=(http_url, save_path, alias,))
            # p.start()
            # p.join()
            self.__download_pool.apply_async(self.download_util.download, args=(http_url, save_path, download_size, referer,))
            log.info("添加到进程池完成，" + save_path)
        else:
            log.info("同步下载")
            self.download_util.download(http_url, save_path, download_size, referer)

    def all_continue_download(self, cache_file_dir=None):
        """
        未完成的文件全部自动下载
        必须等进程池执行完后才能终止主(用户)进程, 调用 close(True)方法可以达到效果
        :return:
        """
        # cache_dir = self.download_cache_path
        cache_dir = self.download_util.download_cache_path
        if cache_file_dir is not None:
            cache_dir = cache_file_dir
        cache_files = os.listdir(cache_dir)
        for cache_file in cache_files:
            cache_file_path = os.path.join(cache_dir, cache_file)
            # 打开一个进程调用下载
            # p = Process(target=self.__download_file(cache_file_path))
            # p = Process(target=self.download_util.contains_download, args=(None, cache_file_path))
            # p.start()
            self.__download_pool.apply_async(self.download_util.contains_download, args=(None, cache_file_path,))

    def contains_download(self, cache_name: str = None, cache_path: str = None):
        """
        继续下载单个文件
        :param cache_name: 缓存文件名
        :param cache_path: 缓存文件路径
        :return:
        """
        self.download_util.contains_download(cache_name, cache_path)

    def stop_download(self, cache_file_name: str = None, cache_path: str = None):
        self.download_util.stop_download(cache_file_name, cache_path)

    def del_cache(self):
        self.__del_cache()
        self.download_util.del_cache()

    def __del_cache(self):
        delete_cache(self.download_cache_path, self.request_cache_effective_time)

    def close(self, is_join: bool):
        """
        用户必须手动调用该方法
        :param is_join:
        :return:
        """
        if is_join:
            self.__download_pool.close()
            self.__download_pool.join()

    def test(self):
        log.info("fuck %s", r'you')


def md5(content):
    md5 = hashlib.md5()
    md5.update(content.encode(r"utf-8"))
    return md5.hexdigest()


def delete_cache(cache_path: str, effective_time: int):
    if os.path.exists(cache_path):
        cache_list = os.listdir(cache_path)
        for cache_file in cache_list:
            cache_file_path = os.path.join(cache_path, cache_file)
            if not os.path.isdir(cache_file_path):
                create_time = os.path.getmtime(cache_file_path)
                now = time.time()
                if now - create_time > effective_time:
                    os.remove(cache_file_path)


if __name__ == '__main__':
    http_client = WindowsChrome(enable_request_cache=False, request_cache_effective_time=10)
    # http_client.test()
    # print(http_client.test2())
    html = http_client.get(
        'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-21790579165.3.4f007b7dM5WM1x&id=36518101636&scene=taobao_shop',
        encoding="UTF-8")
    print(html)  # print(html)
    # html = http_client.get('https://www.baidu.com')
    # print(html)
    # print(html)
    # print('html = ' + html)
