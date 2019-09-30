import re
import json
import time
import requests
from requests.exceptions import RequestException


def get_one_page(url):
    """请求单页，获取HTML文档"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    """正则提取HTML中的电影信息"""
    if not html:
        return []
    pattern = re.compile(r'<dd>.*?>(\d+)</i>.*?<img data-src="(.*?)".*?"name">.*?>(.*?)</a>'
                         r'.*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>'
                         r'.*?fraction">(.*?)</i>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2].strip(),
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6],
        }


def write_to_file(content):
    """将电影信息写入文件"""
    if not content:
        return
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False)+'\n')


def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    for i in range(10):
        main(i*10)
        time.sleep(1)
