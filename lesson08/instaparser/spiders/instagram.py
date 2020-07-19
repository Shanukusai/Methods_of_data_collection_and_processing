# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    # атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'spam.margo2020'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1595176990:AdVQAD1v6Ns2Qo+2zoaSjceGv2Kz2tl63JMxsK2MiiLiID5acbeqlrxZkokwsUY85k4GtalGrqWp06fitxZCGO0IvyK5j0nDIiIVemUlVk3YPED7QRTrQ+RdV97oJ873oxy7p7OCmG309tJzzQ=='
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    parse_user = ['ai_machine_learning', 'learn.machinelearning']  # Пользователи, у которого собираем посты
    subscriber_status = [1, 0]  # Является или не является подписчиком

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    subscribers_hash = 'c76146de99bb02f6415203be841dd25a'  # hash для получения списка подписчиков
    subscriptions_hash = 'd04b0a864b4b54837c0d870b0e77e076'  # hash для получения списка подписок

    def parse(self, response: HtmlResponse):  # Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:  # Проверяем ответ после авторизации
            for status in self.subscriber_status:

                # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                for user in self.parse_user:
                    if status:
                        yield response.follow(
                            f'/{user}',
                            callback=self.user_data_parse,
                            cb_kwargs={'username': user,
                                       's_hash': self.subscribers_hash,
                                       'page_info_get': 'edge_followed_by',
                                       'status': status
                                       }
                        )
                    else:
                        yield response.follow(
                            f'/{user}',
                            callback=self.user_data_parse,
                            cb_kwargs={'username': user,
                                       's_hash': self.subscriptions_hash,
                                       'page_info_get': 'edge_followed',
                                       'status': status
                                       }
                        )

    def user_data_parse(self, response: HtmlResponse, username, s_hash, page_info_get, status):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 подписчиков. Можно больше (макс. 50)
        # Формируем ссылку для получения данных о подписчиках
        url_subscribers = f'{self.graphql_url}query_hash={s_hash}&{urlencode(variables)}'
        yield response.follow(
            url_subscribers,
            callback=self.user_subscrib_parse,
            cb_kwargs={'username': username,
                       's_hash': s_hash,
                       'page_info_get': page_info_get,
                       'status': status,
                       'user_id': user_id,
                       'variables': deepcopy(variables)  # variables ч/з deepcopy во избежание гонок
                       }
        )

    # Принимаем ответ. Не забываем про параметры от cb_kwargs
    def user_subscrib_parse(self, response: HtmlResponse, username, user_id, variables, s_hash, page_info_get, status):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get(page_info_get).get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_subscrib = f'{self.graphql_url}query_hash={s_hash}&{urlencode(variables)}'
            yield response.follow(
                url_subscrib,
                callback=self.user_subscrib_parse,
                cb_kwargs={'username': username,
                           's_hash': s_hash,
                           'page_info_get': page_info_get,
                           'status': status,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        subscribs = j_data.get('data').get('user').get(page_info_get).get('edges')  # Сами подписчики
        for subscrib in subscribs:  # Перебираем посты, собираем данные
            item = InstaparserItem(
                user_id=user_id,
                subscriber_status=status,
                id=subscrib['node']['id'],
                name=subscrib['node']['username'],
                photo=subscrib['node']['profile_pic_url'],
                full_info=subscrib['node'],
                _id=user_id + subscrib['node']['id']
            )
        yield item  # В пайплайн

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
