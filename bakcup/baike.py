from util.HttpClient import WindowsChrome
from bs4 import BeautifulSoup
import os
import time
import random
import json
from multiprocessing import Pool, Process, Manager
import threading
from typing import List

work_dir = r'D:\work\baike'
# work_dir = r'/root/czh/baike'
cache_dir = os.path.join(work_dir, 'cache')
detail_cache_dir = os.path.join(cache_dir, 'detail')
search_cache_dir = os.path.join(cache_dir, 'search')
success_path = os.path.join(work_dir, r'success.txt')
fail_path = os.path.join(work_dir, r'fail.txt')
not_found_path = os.path.join(work_dir, r'not_found.txt')
sql_path = os.path.join(work_dir, 'city.sql')
match_multiple_path = os.path.join(work_dir, 'match_multiple.txt')
error_path = os.path.join(work_dir, 'error.txt')
# success_file = None
# fail_file = None
# not_found_file = None
# sql_file = None
# match_multiple_file = None
# error_file = None
search_base_url = r'https://www.baike.com/search?keyword='
detail_base_url = r'https://www.baike.com/wikiid/'
http_client: WindowsChrome = None
comm = r','
desc_header = r'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport" /><meta content="width=device-width, target-densitydpi=320, user-scalable=no" name="viewport" /><meta content="yes" name="apple-mobile-web-app-capable"><meta content="black" name="apple-mobile-web-app-status-bar-style"><meta content="telephone=no" name="format-detection"><link  href="https://image.huaxiafengwu.com/tinymce-style.css?v=1596632779563" rel="stylesheet" type="text/css" /><script src="https://image.huaxiafengwu.com/js/lazysizes.min.js?v=5.2.1" async=""></script></head><body class="content">'
desc_footer = r'</body></html>'
lock = threading.Lock()
success_file = open(success_path, 'w', encoding='UTF-8')
fail_file = open(fail_path, 'w', encoding='UTF-8')
not_found_file = open(not_found_path, 'w', encoding='UTF-8')
sql_file = open(sql_path, 'w', encoding='UTF-8')
match_multiple_file = open(match_multiple_path, 'w', encoding='UTF-8')
error_file = open(error_path, 'w', encoding='UTF-8')


def init():
    """
    初始化
    """
    __create_dir(work_dir)
    __create_dir(cache_dir)
    __create_dir(detail_cache_dir)
    __create_dir(search_cache_dir)
    global success_file
    global fail_file
    global not_found_file
    global sql_file
    global match_multiple_file
    global error_file
    global http_client
    # success_file = open(success_path, 'w', encoding='UTF-8')
    # fail_file = open(fail_path, 'w', encoding='UTF-8')
    # not_found_file = open(not_found_path, 'w', encoding='UTF-8')
    # sql_file = open(sql_path, 'w', encoding='UTF-8')
    # match_multiple_file = open(match_multiple_path, 'w', encoding='UTF-8')
    # error_file = open(error_path, 'w', encoding='UTF-8')
    http_client = WindowsChrome()


def __create_dir(file_path):
    if not os.path.exists(file_path):
        os.mkdir(file_path)


def search(keyword: str, retry: int = 10) -> dict:
    """
    百科搜索
    keyword: 关键字
    retry: 重试次数
    """
    global http_client
    search_url = search_base_url + keyword
    cache_path = os.path.join(search_cache_dir, keyword + '.html')
    cache_path_is_exists = os.path.exists(cache_path)
    if cache_path_is_exists:
        print('keyword: ' + keyword + "，从缓存中读取数据")
        html = __read_cache(cache_path)
    else:
        print(search_url)
        print('keyword: ' + keyword + "，从网络中读取数据")
        html = http_client.get(search_url, encoding='UTF-8')
    if html != '':
        # 初始化soup
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find('body').find_all('script')

        if len(scripts) > 0:
            script_html = scripts[0].string
            # json 数据在第二个 { 和 倒数第二个 } 中间
            l_index = script_html.find(r'{', script_html.find(r'{') + 1)
            r_index = script_html.rfind(r'}', 0, script_html.rfind(r'}') - 1)
            ret = script_html[l_index: r_index + 1]
            search_ret = json.loads(ret)
            if 'WikiDoc' in search_ret or 'Exact' in search_ret:
                print('keyword: ' + keyword + '找到了data')
                __save_cache(cache_path, html)
                return search_ret
            if script_html.find('Redirecting to') >= 0:
                a_tag = soup.find('a')
                wikiId = a_tag.string.replace('/wikiid/', '').replace('?', '')
                print('keyword: ' + keyword + '需要重定向，wikiId: ' + wikiId)
                if wikiId != '':
                    __save_cache(cache_path, html)
                    return {'wikiId': wikiId}
    error_file.write('html为空' + comm + ', keyword: ' + keyword)
    # __file_write(error_file, 'html为空' + comm + ', keyword: ' + keyword)
    if retry > 0 and not cache_path_is_exists:
        sleep_seconds = random.randint(0, 4)
        retry = retry - 1
        print('正在重试，还有重试机会：' + str(retry) + ", 停顿" + str(sleep_seconds) + "秒")
        time.sleep(sleep_seconds)
        return search(keyword, retry)
    else:
        __delete_cache(cache_path)
        return None


def detail(wiki_id: str) -> dict:
    """
    获取详情
    """
    detail_url = detail_base_url + wiki_id
    cache_file = os.path.join(detail_cache_dir, wiki_id + '.html')
    if os.path.exists(cache_file):
        print('wikiId: ' + wiki_id + '，从缓存中读取数据')
        html = __read_cache(cache_file)
    else:
        print(detail_url)
        print('wikiId: ' + wiki_id + '，从网络中读取数据')
        html = http_client.get(detail_url, encoding='UTF-8')
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find('body').find_all('script')
    if len(scripts) > 0:
        script_html = scripts[0].string
        # json 数据在第二个 { 和 倒数第二个 } 中间
        l_index = script_html.find(r'{', script_html.find(r'{') + 1)
        r_index = script_html.rfind(r'}', 0, script_html.rfind(r'}') - 1)
        ret = script_html[l_index: r_index + 1]
        __save_cache(cache_file, html)
        return json.loads(ret)
    return None


def parse_abstract_2_html(abstract: List[dict]) -> str:
    p_tags = ''
    for paragraph in abstract:
        p_tags = p_tags + r'<p>'
        # print(paragraph)
        if 'content' in paragraph:
            for content_item in paragraph['content']:
                if 'text' in content_item:
                    p_tags = p_tags + content_item['text']
                elif 'content' in content_item and 'text' in content_item['content'][0]:
                    p_tags = p_tags + content_item['content'][0]['text']
        p_tags = p_tags + r'</p>'
    return p_tags


def __save_cache(file_path: str, content: str) -> None:
    with open(file_path, 'w', encoding='UTF-8') as f:
        f.write(content)


def __read_cache(file_path: str) -> str:
    with open(file_path, 'r', encoding='UTF-8') as f:
        return f.read()


def __delete_cache(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)


def process_city(code: str, name: str, alias: str, need_retry: bool) -> None:
    global success_file
    global fail_file
    global not_found_file
    global sql_file
    global match_multiple_file
    search_result = search(alias)
    if search_result is None:
        fail_file.write(code + comm + name + comm + '解析失败\n')
        return
    if 'Exact' not in search_result and 'WikiDoc' not in search_result and 'WikiId' not in search_result:
        fail_file.write(code + comm + name + comm + 'data为空，详情未找到\n')
        # __file_write(fail_file, code + comm + name + comm + 'data为空，详情未找到\n')
    if 'WikiDoc' in search_result:
        # 直接返回搜索结果
        wiki_detail = search_result
    else:
        if 'WikiId' in search_result:
            wiki_id = search_result['WikiId']
        elif search_result['Exact']:
            # 精确匹配
            wiki_id = search_result['WikiDocList'][0]['WikiDocID']
            match_multiple_file.write(code + comm + name + comm + (detail_base_url + wiki_id) + '\n')
            # __file_write(match_multiple_file, code + comm + name + comm + (detail_base_url + wiki_id) + '\n')
        else:
            # 匹配失败，判断是否需要去尾匹配
            if need_retry:
                if name.find(r'特别行政区') >= 0:
                    new_alias = alias.replace(r'特别行政区', '')
                else:
                    new_alias = alias[:-1]
                return process_city(code, name, new_alias, False)
            else:
                not_found_file.write(code + comm + name)
                # __file_write(not_found_file, code + comm + name)
                return
        wiki_detail = detail(wiki_id)
    if wiki_detail is None:
        fail_file.write(code + comm + name + comm + "详情未找到\n")
        # __file_write(fail_file, code + comm + name + comm + "详情未找到\n")
    try:
        # print(wiki_detail)
        wiki_abstract = wiki_detail['WikiDoc']['Abstract']
        desc = parse_abstract_2_html(json.loads(wiki_abstract))
        sql = __generate_sql(desc, code)
        sql_file.write(sql + '\n')
        success_file.write(code + comm + name + '\n')
        # __file_write(sql_file, sql + '\n')
        # __file_write(success_file, code + comm + name + '\n')
    except KeyError:
        fail_file.write(code + comm + name + comm + '解析wikiDetail出错\n')
        # __file_write(fail_file, code + comm + name + comm + '解析wikiDetail出错\n')
        print('解析出错', wiki_detail)


def __generate_sql(desc: str, code: str) -> str:
    desc = desc.replace(r"'", r"''")
    sql_template = r"update city_info.city set description = '{desc}' where code = {code} and city.description is null or trim(city.description) = '';"
    return sql_template.format(desc=desc, code=code)


def process_city_all_city_from_file(file_path: str):
    city_txt = __read_cache(file_path)
    __process_city_all_city(city_txt)


def process_city_all_city_from_url(url: str):
    city_txt = http_client.get(url, encoding='UTF-8')
    __process_city_all_city(city_txt)
    # __process_city_all_city_pool(city_txt)


def __process_city_all_city(city_txt: str):
    city_list = city_txt.split('\n')
    index = 1
    for city in city_list:
        print('正在处理第' + str(index) + ', 总共' + str(len(city_list)) + '个城市')
        index = index + 1
        city_info = city.split(r'.')
        if len(city_info) > 1:
            process_city(city_info[0], city_info[1], city_info[1], True)


def __process_city_all_city_pool(city_txt: str):
    """
    并发执行
    """
    # p_pool = Pool(processes=10)
    p_list = []
    city_list = city_txt.split('\n')
    index = 1
    for city in city_list[0: 5]:
        print('正在处理第' + str(index) + ', 总共' + str(len(city_list)) + '个城市')
        index = index + 1
        city_info = city.split(r'.')
        # process_city(city_info[0], city_info[1], city_info[1], True)
        # p_pool.apply_async(process_city, args=(city_info[0], city_info[1], city_info[1], True))
        p = Process(target=process_city, args=(city_info[0], city_info[1], city_info[1], True))
        p_list.append(p)
        p.start()
    for p in p_list:
        p.join()


def __file_write(file, content):
    lock.acquire()
    print('锁。。。。。。')
    file.write(content)
    print(content)
    print('释放锁')
    lock.release()


def close():
    global success_file
    global fail_file
    global not_found_file
    global sql_file
    global match_multiple_file
    global error_file
    success_file.close()
    fail_file.close()
    not_found_file.close()
    sql_file.close()
    match_multiple_file.close()
    error_file.close()


if __name__ == '__main__':
    init()
    # process_city('111', '北京市', '北京', True)
    start_time = time.time()
    # process_city_all_city_from_file(r'D:\work\baike\city.txt')
    process_city_all_city_from_url(r'http://www.hywdyy.top/city.txt')
    end_time = time.time()
    print('耗时: ' + str(end_time - start_time))
    close()
