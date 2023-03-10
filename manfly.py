from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup
import os
import json

""" 漫画猫 """

spider_dir = r'/Users/chenzhihao/spider_data/progressive'
un_download_amt = 0


def parse_main_page(browser: WindowsChrome):
    page_url = r'https://www.maofly.com/manga/12608.html'
    html = browser.get(page_url, r'utf-8')
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
            download_image(chrome, tag, a_tag.text.replace(' ', ''), a_tag.get('href'))
        print("----")
    print("添加下载结束")


def download_image(browser: WindowsChrome, tag: str, title: str, url: str):
    global un_download_amt
    save_dir = os.path.join(spider_dir, tag, title)
    image_base_url = r'https://mao.mhtupian.com/uploads/'
    html = browser.get(url, 'utf-8')
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
                save_path = os.path.join(save_dir, __get_file_name(index) + ".jpg")
                if not os.path.exists(save_path):
                    print("未下载图片：" + save_path + ', ' + url + ', ' + final_image_url)
                    un_download_amt = un_download_amt + 1
                    chrome.download(final_image_url, save_path, download_size=10, sync=False)
                # if os.path.exists(save_path):
                #     if os.stat(save_path).st_size == 970:
                #         print('下载失败的路径: ' + save_path)
                #         os.remove(save_path)
                index = index + 1


def __get_file_name(index: int) -> str:
    if index < 10:
        return str(0) + str(0) + str(index)
    elif index < 100:
        return str(0) + str(index)
    else:
        return str(index)


def test_parse_base_data(browser: WindowsChrome):
    url = r'https://www.maofly.com/manga/12608/83703.html'
    html = browser.get(url, 'utf-8')
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
            for image_url in image_url_list:
                print(image_url)
                pass


if __name__ == '__main__':
    # /Users/chenzhihao/spider_data
    chrome = WindowsChrome(max_download_num=24, enable_request_cache=True, request_cache_effective_time=360000)
    # download_image(chrome, "番外", "11", "https://www.maofly.com/manga/17393/117262.html")
    # parse_main_page(chrome)
    # test_parse_base_data(chrome)
    # print(os.path.join(spider_dir, "test", "a"))
    parse_main_page(chrome)
    chrome.close(True)
    # print(un_download_amt)