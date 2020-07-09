# 1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и
# сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options
from pprint import pprint
import time

client = MongoClient('localhost', 27017)
db = client['mail']
c_mail = db.mail

chrome_options = Options()
chrome_options.add_argument('start-maximized')  #--headless
driver = webdriver.Chrome('.\chromedriver.exe', options=chrome_options)

driver.get('https://mail.ru/')
elem = driver.find_element_by_id('mailbox:login')
elem.send_keys('study.ai_172@mail.ru')

enter_button = driver.find_element_by_css_selector(
    'input[class="o-control"]'
)

enter_button.click()

time.sleep(0.9)
elem = driver.find_element_by_id('mailbox:password')
elem.send_keys('NextPassword172')

enter_button = driver.find_element_by_id('mailbox:submit')
enter_button.click()

time.sleep(5)
first_mail = driver.find_element_by_class_name('js-letter-list-item')
first_mail.click()

while True:
    try:
        mail = {}

        # Так надо =(
        time.sleep(1)

        mail['_id'] = driver.find_element_by_class_name('thread__letter').get_attribute('data-id')
        mail['contact'] = driver.find_element_by_class_name('letter-contact').get_attribute('title') + ' ' + \
        driver.find_element_by_class_name('letter-contact').text
        mail['date'] = driver.find_element_by_class_name('letter__date').text
        mail['subject'] = driver.find_element_by_class_name('thread__subject').text
        mail['text'] = driver.find_element_by_class_name('letter__body').text

        c_mail.replace_one({'_id': mail['_id']}, mail, True)

        # Так надо =(
        time.sleep(1)
        button_next = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'svg[class="ico ico_16-arrow-down ico_size_s"]')))
        button_next.click()
    except exceptions.ElementClickInterceptedException:
        print('Закончили')
        break

driver.quit()

for i in c_mail.find({}):
    pprint(i)






