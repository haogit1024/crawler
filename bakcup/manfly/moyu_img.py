#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""摸鱼图库爬虫"""

from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup
import os

MAIN_LINK = r'https://52996.me/photos/series-%E7%A7%80%E4%BA%BA%E7%BD%91.html'
BASE_URL = r'https://52996.me'
BASE_DOWNLOAD_PATH = os.path.join(os.environ['HOME'], 'spider_data')


def get_tab_links(chrome: WindowsChrome):
    html = chrome.get(MAIN_LINK, 'utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    series_divs = soup.findAll('div', attrs={'class': 'series'})
    link_divs = series_divs[1]
    a_tags = link_divs.findAll('a')
    res = []
    for a in a_tags[1:]:
        res.append(BASE_URL + a.get('href'))
    return res


def download_tab(chrome: WindowsChrome, tab_link: str, tab_name: str, index: int = 1):
    """
    下载一个tab的所有图片
    1. 解析这一页的html获取一个写真的url
    2. 获取下一页的url
    """
    if index >= 50:
        # 暂时先下载前50页
        return
    html = chrome.get(tab_link, 'utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    list_div = soup.find('div', attrs={'class': 'list'})
    # print(list_div)
    item_divs = list_div.findAll('div', attrs={'class': 'item'})
    # print(item_divs)
    j = 0
    for item_div in item_divs:
        j = j + 1
        a_tag = item_div.find("a")
        # print(a_tag)
        a_tag_img = a_tag.find('img')
        alt: str = a_tag_img.get('alt')
        alt_array = alt.split(" ")
        person_name = alt_array[len(alt_array) - 1]
        item_url = BASE_URL + a_tag.get('href')
        download_dir_path = os.path.join(BASE_DOWNLOAD_PATH, tab_name, str(index) + r'_' + str(j) + person_name)
        if not os.path.exists(download_dir_path):
            download_tab_item(chrome, item_url, download_dir_path)
        # print(download_dir_path)
    # 获取分页
    pager_div = soup.find('div', attrs={'class': 'pager'})
    next_page_a_tag = pager_div.find('a', attrs={'class': 'next'})
    # print(next_page_a_tag)
    # print("----------")
    next_href = next_page_a_tag.get('href')
    if next_href is not None:
        index = index + 1
        download_tab(chrome, BASE_URL + next_href, tab_name, index)


def download_tab_item(chrome: WindowsChrome, item_link: str, download_dir_path: str):
    """
    下载单个写真集
    1. 获取图片url
    2. 如果有下一页继续解析下载
    """
    html = chrome.get(item_link, 'utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    photos_div = soup.find('div', attrs={'class': 'photos'})
    figure_list = photos_div.findAll('figure')
    # print(figure_list)
    for figure in figure_list:
        style = figure.get('style')
        f_index = style.index(r"url('") + 5
        l_index = style.index(r"');")
        url: str = style[f_index: l_index]
        # https://img.xchina.fun/photos/62c2fbea80afb/0001_600x0.jpg, 去掉_600x0
        url = url.replace(r'_600x0', '')
        url_items = url.split(r'/')
        file_name = url_items[len(url_items) - 1]
        final_download_path = os.path.join(download_dir_path, file_name)
        chrome.download(url, final_download_path, download_size=200, sync=True)
    # 获取下一页
    # print("---------------")
    pager_div = soup.find('div', attrs={'class': 'pager'})
    next_page_a_tag = pager_div.find('a', attrs={'class': 'next'})
    if next_page_a_tag is not None:
        next_href = next_page_a_tag.get('href')
        if next_href is not None:
            download_tab_item(chrome, BASE_URL + next_href, download_dir_path)


def test(chrome: WindowsChrome):
    # tab_links = get_tab_links(chrome)
    # print(tab_links)
    download_tab(chrome, MAIN_LINK, '测试')
    # item_link = r'https://52996.me/photo/id-62c2fbea80afb.html'
    # download_tab_item(chrome, item_link, '测试')


def main():
    chrome = WindowsChrome(enable_request_cache=True, request_cache_effective_time=3600 * 24 * 30)
    tab_links = get_tab_links(chrome)
    for tab_link in tab_links:
        # print(tab_link)
        tab_name = tab_link.replace('https://52996.me/photos/series-', '')
        tab_name = tab_name.replace(r'.html', '')
        download_tab(chrome, tab_link, tab_name)


if __name__ == '__main__':
    print(BASE_DOWNLOAD_PATH)
    main()
