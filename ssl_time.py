import re
import subprocess
from datetime import datetime


def get_re_match_result(pattern: str, string: str) -> str:
    match = re.search(pattern, string)
    return match.group(1)


def parse_time(date_str: str) -> str:
    print(date_str)
    print(type(date_str))
    # Dec  5 00:00:00 2023 GMT
    GMT_FORMAT = r'%b  %d %H:%M:%S %Y GMT'
    # return datetime.strftime(date_str, "%Y-%m-%d %H:%M:%S")
    return datetime.strptime(date_str, GMT_FORMAT)


def get_cert_info(domain: str) -> dict:
    cmd = f'curl -Ivs https://{domain}'
    exitcode, output = subprocess.getstatusoutput(cmd)
    print(f'exitcode={exitcode}')
    # 正则匹配
    start_date = get_re_match_result('start date: (.*)', output)
    expire_date = get_re_match_result('expire date: (.*)', output)

    # 解析匹配结果
    start_date = parse_time(start_date)
    expire_date = parse_time(expire_date)

    return start_date, expire_date


def get_cert_expire_date(domain: str) -> int:
    """获取证书剩余时间"""
    # info = get_cert_info(domain)

    # expire_date = info['expire_date']
    start_date, expire_date = get_cert_info(domain)

    # 剩余天数
    return (expire_date - datetime.now()).days


if __name__ == "__main__":
    domain = 'api-test.danzhuqiyi.com'
    expire_date = get_cert_expire_date(domain)
    print(expire_date)