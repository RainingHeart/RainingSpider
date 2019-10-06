from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
import pymongo

base_url = 'https://m.weibo.cn/api/container/getIndex?'
max_page = 10


def get_page(page):
    params = {
        'type': 'uid',
        'value': '2830678474',
        'containerid': '1076032830678474',
        'page': page
    }

    url = base_url + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print(e.args)


def parse_page(json):
    if json:
        items = json.get('data').get('cards')
        for item in items:
            item = item.get('mblog')
            weibo = {}
            weibo['id'] = item.get('id')
            weibo['text'] = pq(item.get('text')).text()
            weibo['attitude'] = item.get('attitudes_count')
            weibo['comments'] = item.get('comments_count')
            weibo['reposts'] = item.get('reposts_count')
            yield weibo


def save_to_mongo(result):
    if collection.insert_one(result):
        print('Saved to Mongo')


if __name__ == '__main__':
    client = pymongo.MongoClient(host='localhost', port=27017)
    collection = client.weibo.weibo
    for page in range(1, max_page + 1):
        json = get_page(page)
        results = parse_page(json)
        for result in results:
            print(result)
            save_to_mongo(result)
