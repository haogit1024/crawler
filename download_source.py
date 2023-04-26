import os.path
import re

from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup


# 全局浏览器
# chrome = WindowsChrome(max_download_num=24, enable_request_cache=True, request_cache_effective_time=360000)
# 全局下载路径
download_path = r'/Users/chenzhihao/work_space/danzhuyiqi'
# 网站主路径
domain_path = r'https://www.ruiqichina.com'


def download(url: str, chrome: WindowsChrome):
    html = chrome.get(url, encoding='UTF-8')
    download_img_from_html(html, chrome)
    download_background_image(html, chrome)


def download_img_from_html(html: str, chrome: WindowsChrome):
    soup = BeautifulSoup(html, 'html.parser')
    img_tag_list = soup.findAll('img')
    for img_tag in img_tag_list:
        src = img_tag.get('src')
        if src is not None and src != '':
            print('src：' + src)
            print('download_path：' + download_path)
            save_path = os.path.join(download_path, src[1:])
            image_url = domain_path + src
            print('找到图片：' + image_url)
            print('保存地址：' + save_path)
            # if not os.path.exists(save_path):
            chrome.download(image_url, save_path, download_size=100, sync=False)


def download_background_image(html: str, chrome: WindowsChrome):
    soup = BeautifulSoup(html, 'html.parser')
    tag_list = soup.findAll(style=re.compile('background-image'))
    for tag in tag_list:
        style: str = tag.get('style')
        path = style.replace(r'background-image', '')
        path = path.replace(' url(', '')
        path = path.replace(r');', '')
        print('path', path[2:])
        # print("----------")
        save_path = os.path.join(download_path, path[2:])
        image_url = domain_path + path[1:]
        print('找到图片：' + image_url)
        print('保存地址：' + save_path)
        # if not os.path.exists(save_path):
        chrome.download(image_url, save_path, download_size=100, sync=False)


if __name__ == '__main__':
    chrome = WindowsChrome(max_download_num=24, enable_request_cache=True, request_cache_effective_time=360000)
    download('https://www.ruiqichina.com/Recruitment/index.html', chrome)
    chrome.close(True)

