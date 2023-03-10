from abc import ABCMeta, abstractmethod


class DownLoadFile(object, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, http_url, download_path, base_http_client, alias=None,):
        """
        :param http_url: 文件http连接
        :param download_path: 保存到系统的路径
        :param alias: 别名
        :param base_http_client
        """
        pass

    @abstractmethod
    def start_download(self):
        pass


class ImageFile(DownLoadFile):
    def __init__(self, http_url, download_path, base_http_client, alias):
        self.http_url = http_url
        self.download_path = download_path
        self.baseHttpClient = base_http_client
        self.alias = alias

    def start_download(self):
        self.baseHttpClient.download(self.http_url, self.download_path, self.alias)


if __name__ == '__main__':
    from util.HttpClient import WindowsChrome
    httpClient = WindowsChrome()
    http_url = 'https://pic3.zhimg.com/v2-ec1d6a1ef8f7c30eabaf028eb598ca03_b.jpg'
    download_path = 'F:\\迅雷下载\\a.jpg'
    imageFile = ImageFile(http_url, download_path, httpClient, None)
    imageFile.start_download()
