import time
import os
from hashlib import md5
from multiprocessing.pool import Pool
from urllib.parse import urlencode
import requests


GROUP_START = 1
GROUP_END = 20
base_url = 'https://www.toutiao.com/api/search/content/?'


def get_page(offset):
    params = {
        'aid': 24,
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': 20,
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': str(time.time())[0:14].replace('.', '')
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'cookie': 'tt_webid=6744690116542334472; s_v_web_id=5b54f560dd8dd8a8a9cad30d3c31f520; '
                  'WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6744690116542334472; '
                  'csrftoken=f05cbcd142ebb3b187255cb861fc7e42; __tasessionId=3bf84ja4z1570373237278'
    }

    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print(e.args)


def get_images(json):
    if json:
        items = json.get('data')
        if not items:
            return
        for item in items:
            if item.get('abstract') is None:
                continue
            title = item.get('title')
            images = item.get('image_list')
            for image in images:
                yield {
                    'title': title,
                    'image': image.get('url'),
                }


def save_image(item):
    map_table = str.maketrans(r'\/:*?"<>|', '123456789')
    title = item.get('title').translate(map_table)
    if not os.path.exists(title):
        os.mkdir(title)
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(title, md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError as e:
        print('Failed to Save Image')


def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)


if __name__ == '__main__':
    pool = Pool()
    groups = [x * 20 for x in range(GROUP_START, GROUP_END + 1)]
    pool.map(main, groups)
    pool.close()
    pool.join()
