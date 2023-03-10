from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup
import os

base_url = r'https://m.dongman.la/manhua/detail/639/'
download_dir = r'D:\spider_file\gto'
# https://m.dongman.la/manhua/chapter/639/57504/1.html
# https://i2.dongman.la/file/comicbook/g/gtomljs/1/0002.png
# #nextChap


def main():
    chrome = WindowsChrome(max_download_num=24, enable_request_cache=True, request_cache_effective_time=360000)
    # html = chrome.get(base_url, 'utf-8')
    # print(html)
    # test(chrome)
    # download_path = os.path.join(download_dir, '第一章')
    # run(chrome, r'https://m.dongman.la/manhua/chapter/639/57504/1.html', download_path, 0)
    index = 1
    start = 57504
    while start <= 57528:
        url = 'https://m.dongman.la/manhua/chapter/639/' + str(start) + '/1.html'
        download_path = os.path.join(download_dir, '第' + str(index) + '章')
        try:
            run(chrome, url, download_path, index)
        except RuntimeError as e:
            print(e)
        index = index + 1
        start = start + 1
    chrome.close(True)


def run(chrome: WindowsChrome, url, download_path, index):
    html = chrome.get(url, 'utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    image_div = soup.find('div', attrs={'class': 'uk-container uk-container-small'})
    a_tag = image_div.find('a')
    img_tag = image_div.find('img')
    next_link = a_tag.get('href')
    src_link = img_tag.get('src')
    image_download_path = os.path.join(download_path, str(index) + r'.png')
    chrome.download(src_link, image_download_path, download_size=100, sync=True)
    if next_link != '#nextChap':
        index = index + 1
        try:
            run(chrome, next_link, download_path, index)
        except RuntimeError as e:
            print(e)


def test(chrome):
    url = r'https://m.dongman.la/manhua/chapter/639/57504/1.html'
    html = chrome.get(url, 'utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    image_div = soup.find('div', attrs={'class': 'uk-container uk-container-small'})
    # print(image_div)
    a_tag = image_div.find('a')
    img_tag = image_div.find('img')
    print(a_tag.get('href'))
    print(img_tag.get('src'))


if __name__ == '__main__':
    main()
