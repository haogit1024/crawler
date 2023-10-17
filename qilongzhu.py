from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup
import os


base_dir = r'./spider_data'
if not os.path.exists(base_dir):
    os.mkdir(base_dir)


def get_volumes(chrome: WindowsChrome) -> dict[str, str]:
    url = r'http://comic.dragonballcn.com/dragonball_zh_tw.htm'
    html = chrome.get(url, encoding='UTF-8')
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    hdnavli6_divs = soup.findAll('div', attrs={'id': 'hdnavli2'})
    # print(hdnavli6_divs)
    hdnavli6_div_lis = []
    for div in hdnavli6_divs:
        lis = div.findAll('li')
        for li in lis:
            hdnavli6_div_lis.append(li)
    resp = {}
    for li in hdnavli6_div_lis:
        a_tag = li.find('a')
        if a_tag is None:
            continue
        title = a_tag.text
        link = a_tag.get('href')
        resp[title] = link
    return resp


def parse_volume(chrome: WindowsChrome, title: str, link: str):
    save_dir = os.path.join(base_dir, title)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    url = r'http://comic.dragonballcn.com/' + link
    html = chrome.get(url, encoding='UTF-8')
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    file_list = soup.findAll('li', attrs={'class': 'ListItem'})
    for file_item in file_list:
        a_tag = file_item.find('a')
        if a_tag is None:
            continue
        file_link = a_tag.get('href')
        file_url = get_image_url(chrome, file_link)
        file_name = os.path.basename(file_url)
        save_path = os.path.join(save_dir, file_name)
        chrome.download(file_url, save_path)


def get_image_url(chrome: WindowsChrome, link: str):
    url = r'http://comic.dragonballcn.com/list/' + link
    # print('url', url)
    html = chrome.get(url, encoding='UTF-8')
    # print('html', html)
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', attrs={'class': 'DisplayItem'})
    # print(div)
    input_tag = div.find('input')
    # print(input_tag)
    img_tag_html = input_tag.get('value')
    # print(img_tag_html)
    image_soup = BeautifulSoup(img_tag_html, 'html.parser')
    url = image_soup.find('img')
    return url.get('src')


if __name__ == '__main__':
    print("run.....")
    chrome = WindowsChrome(max_download_num=1, enable_request_cache=True, request_cache_effective_time=36000)
    volume_map = get_volumes(chrome)
    for key in volume_map.keys():
        parse_volume(chrome, key, volume_map[key])
    # print(volume_map)
    # parse_volume(chrome, '卷一小悟空和他的伙伴们', 'list/gain_1.php?did=0-3-0')
    # get_image_url(chrome, 'list/gain_1.php?did=0-3-0&fpp=10&fid=1')
    chrome.del_cache()
    chrome.close(is_join=True)
