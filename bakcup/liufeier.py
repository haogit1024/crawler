from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup
import os


download_dir = r'D:\spider_file\liufeier'


def liufeier(url):
    chrome = WindowsChrome(max_download_num=24, enable_request_cache=True, request_cache_effective_time=1800)
    html_parse(chrome, url)
    chrome.close(True)
    print('下载完成')


def html_parse(chrome, url):
    # html = chrome.get(r"https://m.zanyiba.com/zhuanti/liufeier.html", encoding='UTF-8')
    html = chrome.get(url, encoding='UTF-8')
    # html = chrome.get(r"https://m.keaitupian.com/pic/7998.html", encoding='UTF-8')
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.find('div', attrs={'id': 'container'})
    print(item_list)
    a_tag_list = item_list.findAll('a', attrs={'class': 'item_t'})
    # 获取每个写真集的地址
    for a_tag in a_tag_list:
        # print(a_tag)
        # print(a_tag.get('href'))
        # print(a_tag.find('div', attrs={'class': 'title'}).text)
        parse_photo_set_link(chrome, a_tag.get('href'), a_tag.find('div', attrs={'class': 'title'}).text)
    # 获取下一页
    next_page = soup.find('a', attrs={'class': 'next_p'})
    # print('next_page')
    # print(next_page.get('href'))
    if next_page is not None:
        html_parse(chrome, next_page.get('href'))


def parse_photo_set_link(chrome, photo_set_link, link_title, recursion_num=0):
    recursion_num = recursion_num + 1
    html = chrome.get(photo_set_link, encoding='UTF-8')
    # https://m.keaitupian.com
    soup = BeautifulSoup(html, 'html.parser')
    content_pic = soup.find('div', attrs={'id': 'content_pic'})
    bd_div = content_pic.find('div', attrs={'class': 'bd'})
    img_url = bd_div.find('img').get('src')
    print(img_url)
    next_page_url = bd_div.find('a').get('href')
    print(next_page_url)
    print('------')
    download_path = os.path.join(download_dir, link_title, str(recursion_num) + r'.jpg')
    chrome.download(img_url, download_path, download_size=100, sync=True)
    if recursion_num < 100 and next_page_url.find('http') == -1:
        parse_photo_set_link(chrome, r'https://m.keaitupian.com' + next_page_url, link_title, recursion_num)


if __name__ == '__main__':
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    liufeier(r"https://m.keaitupian.com/zt/liufeier/")
