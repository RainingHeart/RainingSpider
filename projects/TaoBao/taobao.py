import json
import time

from pyquery.pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
import pymongo

KEYWORD = 'iPad'
MAX_PAGE = 100

MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_COLLECTION = 'products'


def index_page(page):
    """
    抓取索引页
    :param page: int 页码
    :return: None
    """
    print('正在爬取第%s页' % page)
    try:
        browser.get(url)
        if page > 1:
            input_el = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#mainsrp-pager div.form>input')))
            submit_el = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#mainsrp-pager div.form>span.btn.J_Submit')
            ))
            input_el.clear()
            input_el.send_keys(page)
            submit_el.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager li.item.active>span'), str(page)))
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.m-itemlist .items .item')
        ))
        # with open('html.html', 'w', encoding='utf-8') as f:
        #     f.write(browser.page_source)
        get_products()
    except TimeoutException as e:
        print(e)


def get_products():
    """提取商品数据"""
    html = browser.page_source
    doc = pq(html)

    items = doc.find('#mainsrp-itemlist .items .item')
    for item in items.items():
        product = {
            'image': item.find('.pic .img').attr('data-src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text(),
        }
        print(product)
        save_to_mongo(product)


def save_to_mongo(product):
    """
    保存至MongoDB
    :param product: 结果
    :return:
    """
    try:
        if db[MONGO_COLLECTION].insert_one(product):
            print('存储到 MongoDB 成功')
    except Exception as e:
        print('存储到 MongoDB 失败', e)


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=chrome_options)

    url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
    browser.get(url)  # 先访问一个url，再add_cookie，否则一直报错invalid domain
    browser.delete_all_cookies()
    time.sleep(1)

    with open('cookies.json') as f:
        cookie_list = json.load(f)
    for cookie in cookie_list:
        if cookie.get('expiry', None):
            cookie['expiry'] = int(cookie['expiry'])
        browser.add_cookie(cookie)
    wait = WebDriverWait(browser, 10)
    client = pymongo.MongoClient(host=MONGO_URL)
    db = client[MONGO_DB]
    for page in range(1, MAX_PAGE+1):
        index_page(page)
