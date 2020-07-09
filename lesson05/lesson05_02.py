# 2) Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
# Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['mvideo']
mvideo = db.mvideo

chrome_options = Options()
chrome_options.add_argument('start-maximized')  #--headless
driver = webdriver.Chrome('.\chromedriver.exe', options=chrome_options)

url = 'https://www.mvideo.ru'
title_site = 'М.Видео'

driver.get(url)

try:
    bestsellers = driver.find_element_by_xpath(
        '//div[contains(text(),"Хиты продаж")]/ancestor::div[@data-init="gtm-push-products"]'
    )
except exceptions.NoSuchElementException:
    print('Хиты продаж не найдены')

while True:
    try:
        next_button = WebDriverWait(bestsellers, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[class="next-btn sel-hits-button-next"]')
            )
        )

        driver.execute_script("$(arguments[0]).click();", next_button)
    except exceptions.TimeoutException:
        print('Сбор данных окончен')
        break

goods = bestsellers.find_elements_by_css_selector('li.gallery-list-item')

good_item = {}
for good in goods:

    good_item['_id'] = good.find_element_by_css_selector(
        'div.c-product-tile') \
        .get_attribute('data-sel').split('-')[2]

    good_item['title'] = good.find_element_by_css_selector(
        'a.sel-product-tile-title') \
        .get_attribute('innerHTML')

    good_item['good_link'] = good.find_element_by_css_selector(
        'a.sel-product-tile-title') \
        .get_attribute('href')

    good_item['price'] = float(
        good.find_element_by_css_selector(
            'div.c-pdp-price__current').get_attribute('innerHTML').replace(
                '&nbsp;', '').replace('¤', ''))

    good_item['image_link'] = good.find_element_by_css_selector(
        'img[class="lazy product-tile-picture__image"]') \
        .get_attribute('src')

    mvideo.replace_one({'_id': good_item['_id']}, good_item, True)
driver.quit()

for i in mvideo.find({}):
    pprint(i)
