import sys
from util.HttpClient import WindowsChrome
from multiprocessing import Pool
import logging, json, re, os

sys.path.append("..")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ZhiHuImage")


class ZhiHuImage(object):
    def __init__(self, question_id, limit=20, folder='images/', processes=20):
        self.download_pool = Pool(processes=processes)
        self.chrome = WindowsChrome()
        self.folder = folder + '/' + str(question_id) + '/'
        self.question_id = question_id
        self.limit = limit
        self.question_url = 'https://www.zhihu.com/question/' + question_id
        self.question_api_url = 'https://www.zhihu.com/api/v4/questions/{question_id}/answers?include=content&' \
                                'limit={limit}&offset={offset}&sort_by=default'

    def run(self, start_page=1, end_page=-1):
        hast_next = True
        while hast_next and (start_page <= end_page or end_page < 0):
            offset = (start_page - 1) * 20
            question_api_url = self.question_api_url.format(question_id=self.question_id, limit=self.limit,
                                                            offset=offset)
            log.info("question_api_url=" + question_api_url)
            pic_list, next_url, hast_next = self.parse_zhihu_api_response(question_api_url)
            save_folder = self.folder + '第' + str(start_page) + '页/'
            self.save_pic_list(pic_list, save_folder)
            start_page += 1
        log.info('获取图片连接完成')
        self.download_pool.close()
        log.info('开始下载图片')
        self.download_pool.join()
        log.info('图片下载结束')

    def parse_zhihu_api_response(self, url):
        response = self.chrome.get(url, encoding='UTF-8')
        if response is None:
            return None, None, False
        json_obj = json.loads(response)
        data = json_obj['data']
        next_url = json_obj['paging']['next']
        is_end = json_obj['paging']['is_end']
        has_end = not is_end
        pic_url_list = {}
        index = 0
        for data_item in data:
            content = data_item['content']
            author_name = data_item['author']['name']
            pic_list = self.parse_content(content)
            pic_url_list[author_name] = pic_list
            index += 1
        return pic_url_list, next_url, has_end

    def parse_content(self, content):
        """
        :param content:
        :return: list
        """
        result = list(set(re.findall(r'data-original="(.+?)"', content)))
        return result

    def save_pic_list(self, urls, folder):
        """
        save pic to hard disk
        :param urls: dick : {'蓝色': [], '陈慕枫': ['https://pic3.zhimg.com/v2-e31933ae5c79e190934dc872504a272a_r.jpg']}
        :param folder: hard disk : images/first/
        :return: None
        """
        index = 0
        for name, url_item in urls.items():
            print('正在下载：' + name)
            print('size: ' + str(len(url_item)))
            if not url_item:
                continue
            real_folder = folder + str(index) + name + '/'
            if not os.path.exists(real_folder):
                os.makedirs(real_folder)
            pic_index = 0
            for url in url_item:
                pic_name = self.__get_url_last_str(url)
                pic_save_path = real_folder + str(pic_index) + "_" + pic_name
                self.download_pool.apply_async(save_task, args=(self.chrome, url, pic_save_path))
                pic_index += 1
            index += 1

    # def save_task(self, pic_url, pic_save_path):
    #     print('开始下载图片, url:' + pic_url)
    #     with open(pic_save_path, 'wb') as f:
    #         # res = self.session.get(url, headers=self.headers)
    #         res = self.chrome.get(pic_url)
    #         f.write(res)
    #         print('writer finish, url: ' + pic_url)

    def __get_url_last_str(self, url):
        url_str = url.split('/')
        return url_str[len(url_str) - 1]


# python 进程池不能调用实例方法, 简直坑爹
def save_task(windows_chrome, pic_url, pic_save_path):
    print('开始下载图片, url:' + pic_url)
    with open(pic_save_path, 'wb') as f:
        # res = self.session.get(url, headers=self.headers)
        res = windows_chrome.get(pic_url)
        f.write(res)
        # print('writer finish, url: ' + pic_url)


if __name__ == '__main__':
    imageCrawler = ZhiHuImage('302378021')
    imageCrawler.run(start_page=1, end_page=1)
