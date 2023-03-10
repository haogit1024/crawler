from zhihu.ZhiHuCrawler import ZhiHuImage


if __name__ == '__main__':
    image = ZhiHuImage('307669236', processes=25)
    image.run(1, 6)
