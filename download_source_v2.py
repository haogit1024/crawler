import os
import sys

from bs4 import BeautifulSoup

from util.HttpClient import WindowsChrome

"""
下载一个网页的静态资源
1. 获取网站的html
2. 解析html获取静态资源
2.1 css 文件
2.2 js 文件
2.3 img标签的文件
2.4 背景图片
"""

def get_http_link(html: str) -> list[str]:
    links: list[str] = []
    bs = BeautifulSoup(html, "html.parser")
    link_tags = bs.findAll('link')
    for link_tag in link_tags:
        href = link_tag.get('href')
        if href is not None and href != '':
            links.append(href)
    script_tags = bs.findAll('script')
    for script_tag in script_tags:
        src = script_tag.get('src')
        if src is not None and src != '':
            links.append(src)
    img_tags = bs.findAll('img')
    for img_tag in img_tags:
        src = img_tag.get('src')
        if src is not None and src != '':
            links.append(src)
    # todo 解析 background 里的 http 链接
    return links

if __name__ == '__main__':
    html_link = 'https://www.ruiqichina.com/Recruitment/index.html'
    http_client = WindowsChrome(enable_request_cache=False)
    html = http_client.get(html_link)
    # print(html)
    links = get_http_link(html)
    print(links)
    domain: str = http_client.get_referer(html_link)
