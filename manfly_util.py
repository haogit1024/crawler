from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup
import os
import json

""" 漫画猫下载工具 """


class Manfly_util(object):
    def __init__(self, chrome: WindowsChrome, spider_dir: str, main_page_url: str):
        self.chrome = chrome
        self.spider_dir = spider_dir
        self.main_page_url = main_page_url
        self.un_download_amt = 0

    def parse_main_page(self):
        page_url = self.main_page_url
        html = self.chrome.get(page_url, r'utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        tab_content_div = soup.find('div', attrs={'id': 'comic-book-list'})
        # 只要单话的番外篇
        tad_pane_divs = tab_content_div.findAll('div', attrs={'class': 'tab-pane'})
        print(len(tad_pane_divs))
        for div in tad_pane_divs:
            title_h2_tag = div.find('h2')
            tag = title_h2_tag.text
            # 漫画地址
            a_tags = div.findAll('a', attrs={'class': 'fixed-a-es'})
            a_tags.reverse()
            for a_tag in a_tags:
                print('link', a_tag.get('href'))
                print('title', a_tag.text.replace(' ', ''))
                self.download_image(tag, a_tag.text.replace(' ', ''), a_tag.get('href'))
            print("----")
        print("添加下载结束")

    def download_image(self, tag: str, title: str, url: str):
        global un_download_amt
        save_dir = os.path.join(self.spider_dir, tag, title)
        image_base_url = r'https://mao.mhtupian.com/uploads/'
        html = self.chrome.get(url, 'utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        script_tag_list = soup.findAll('script')
        for script_tag in script_tag_list:
            script = script_tag.text
            if script.find(r'let img_data') != -1:
                # 获取image_data
                line_list = script.split('\n')
                # let image_data = "aaaa"
                left_index = line_list[1].find('"')
                right_index = line_list[1].rfind('"')
                image_data = line_list[1][left_index + 1: right_index]
                decode_cmd = r'node ddmao_decode.js ' + image_data
                image_info = os.popen(decode_cmd).read()
                image_url_list = json.loads(image_info)
                index = 1
                for image_url in image_url_list:
                    final_image_url = image_base_url + image_url
                    save_path = os.path.join(save_dir, self.__get_file_name(index) + ".jpg")
                    if not os.path.exists(save_path):
                        print("未下载图片：" + save_path + ', ' + url + ', ' + final_image_url)
                        self.un_download_amt = self.un_download_amt + 1
                        self.chrome.download(final_image_url, save_path, download_size=1, sync=True, referer='https://www.maofly.com/')
                    index = index + 1

    def __get_file_name(self, index: int) -> str:
        if index < 10:
            return str(0) + str(0) + str(index)
        elif index < 100:
            return str(0) + str(index)
        else:
            return str(index)


if __name__ == '__main__':
    chrome = WindowsChrome(max_download_num=24, enable_request_cache=True, request_cache_effective_time=360000)
    base_path = './spider_data'
    download_info_list = [
        {
            'url': 'https://www.maofly.com/manga/13296.html',
            'download_path': '黄金小子'
        },
        {
            'url': 'https://www.maofly.com/manga/23394.html',
            'download_path': '龙珠'
        },
        {
            'url': 'https://www.maofly.com/manga/20550.html',
            'download_path': '冥王计划'
        },
        {
            'url': 'https://www.maofly.com/manga/13296.html',
            'download_path': '风筝'
        },
    ]
    for download_info in download_info_list:
        spider_dir = os.path.join(base_path, download_info['download_path'])
        main_page_url = download_info['url']
        print('spider_dir', spider_dir)
        print('url', main_page_url)
        util = Manfly_util(chrome, spider_dir, main_page_url)
        util.parse_main_page()
        # time.sleep(10)
        # util.parse_main_page()
        # time.sleep(10)
        # util.parse_main_page()
    chrome.close(True)