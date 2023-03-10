from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup
import os

home_page = r'https://m.peachring.com/weibo/user/2936497927/'
# home_page = r'https://m.peachring.com/weibo/user/5892748793?next=4067210764225647'
download_dir = r'D:\spider_file'

home_page_list = [
    # 'https://m.peachring.com/weibo/user/3878034792',
    # 'https://m.peachring.com/weibo/user/2936497927',
    # 'https://m.peachring.com/weibo/user/5880532871',
    # 'https://m.peachring.com/weibo/user/5669809845',
    # 'https://m.peachring.com/weibo/user/5404464551',
    # 'https://m.peachring.com/weibo/user/1797407720',
    # 'https://m.peachring.com/weibo/user/5557747699',
    # 'https://m.peachring.com/weibo/user/1684199600',
    # 'https://m.peachring.com/weibo/user/1802027532',
    # 'https://m.peachring.com/weibo/user/1777781560',
    # 'https://m.peachring.com/weibo/user/5786523906',
    # 'https://m.peachring.com/weibo/user/5702310695',
    # 'https://m.peachring.com/weibo/user/5027019119',
    # 'https://m.peachring.com/weibo/user/5175360325',
    # 'https://m.peachring.com/weibo/user/3893571172',
    # 'https://m.peachring.com/weibo/user/2738705003',
    # 'https://m.peachring.com/weibo/user/3717000605',
    # 'https://m.peachring.com/weibo/user/1020572290',
    # 'https://m.peachring.com/weibo/user/3286790770',
    'https://m.peachring.com/weibo/user/5282030469',
]


def download(chrome: WindowsChrome, base_url, url: str):
    html = chrome.get(url, encoding='UTF-8')
    soup = BeautifulSoup(html, 'html.parser')
    img_list = soup.findAll('img', attrs={'class': 'am-img-responsive'})
    date = soup.find('span', attrs={'class': 'time'})
    name = soup.find('p', attrs={'class': 'name'})
    print('name', name)
    if date is None:
        print(url)
        return
    else:
        date = date.text.replace('\n', '').replace(' ', '').replace(':', '')
    if name is None:
        return
    else:
        name = name.text.replace('\n', '').replace(' ', '').replace(':', '')
    print('name', name)
    i = 0
    for img in img_list:
        img_url = img.get('data-rel')
        download_path = os.path.join(download_dir, name, date, str(i) + r'.jpg')
        print('download_path', download_path)
        chrome.download(img_url, download_path, download_size=100, sync=True)
        i = i + 1
    next = soup.find('a', attrs={'class': 'next'})
    if next is not None:
        next_url = base_url + next.get('href')
        print('next_url', next_url)
        download(chrome, base_url, next_url)


if __name__ == '__main__':

    # download(chrome, home_page)
    # download(chrome, home_page_list[0])
    for home_page_item in home_page_list:
        chrome = WindowsChrome(max_download_num=12, enable_request_cache=True, request_cache_effective_time=36000)
        print('home_page_item', home_page_item)
        download(chrome, home_page_item, home_page_item)
        print('下载任务添加完毕')
        chrome.close(True)
        print('chrome close')
