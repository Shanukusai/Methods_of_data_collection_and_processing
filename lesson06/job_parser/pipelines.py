# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from pymongo import MongoClient
import re


class JobParserPipeline(object):
    def __init__(self):
        MONGO_URI = 'mongodb://localhost:27017/'
        MONGO_DATABASE = 'vacancy'

        client = MongoClient(MONGO_URI)
        self.mongo_base = client[MONGO_DATABASE]

    def process_item(self, item, spider):
        if spider.name == 'hh_ru':
            vacancy_name = ''.join(item['name'])
            _id = item['_id']

            for i in item['salary']:
                if item['salary'][0] == 'от ' and item['salary'][2] == ' до ':
                    salary_min = item['salary'][1].replace(u'\xa0', u'')
                    salary_max = item['salary'][3].replace(u'\xa0', u'')
                    salary_currency = item['salary'][5]
                elif item['salary'][0] == 'от ':
                    salary_min = item['salary'][1].replace(u'\xa0', u'')
                    salary_max = None
                    salary_currency = item['salary'][3]
                elif item['salary'][0] == 'до ':
                    salary_min = None
                    salary_max = item['salary'][1].replace(u'\xa0', u'')
                    salary_currency = item['salary'][3]
                else:
                    salary_min = None
                    salary_max = None
                    salary_currency = None

            vacancy_link = item['vacancy_link']
            site_scraping = item['site_scraping']

            vacancy_json = {
                '_id': _id, \
                'vacancy_name': vacancy_name, \
                'salary_min': salary_min, \
                'salary_max': salary_max, \
                'salary_currency': salary_currency, \
                'vacancy_link': vacancy_link, \
                'site_scraping': site_scraping
            }

            collection = self.mongo_base[spider.name]
            # collection.insert_one(vacancy_json)
            collection.replace_one({'_id': vacancy_json['_id']}, vacancy_json, True)
            return vacancy_json
        else:
            vacancy_name = ''.join(item['name'])
            _id = item['_id'][1]

            salary_min = None
            salary_max = None
            salary_currency = None

            for i in item['salary']:
                if item['salary'][0] == 'от':
                    salary_min = re.search(r'\d+', item['salary'][2].replace(u'\xa0', u'')).group(0)
                    salary_max = None
                    salary_currency = re.search(r'\D+',item['salary'][2].replace(u'\xa0', u'')).group(0)
                elif len(item['salary']) == 4:
                    salary_min = item['salary'][0].replace(u'\xa0', u'')
                    salary_max = item['salary'][1].replace(u'\xa0', u'')
                    salary_currency = item['salary'][3]
                elif item['salary'][0] == 'до':
                    salary_min = None
                    salary_max = re.search('\d+',item['salary'][2].replace(u'\xa0', u'')).group(0)
                    salary_currency = re.search('\D+',item['salary'][2].replace(u'\xa0', u'')).group(0)
                else:
                    salary_min = None
                    salary_max = None
                    salary_currency = None

            vacancy_link = item['vacancy_link']
            site_scraping = item['site_scraping']

            vacancy_json = {
                '_id': _id, \
                'vacancy_name': vacancy_name, \
                'salary_min': salary_min, \
                'salary_max': salary_max, \
                'salary_currency': salary_currency, \
                'vacancy_link': vacancy_link, \
                'site_scraping': site_scraping
            }

            collection = self.mongo_base[spider.name]
            # collection.insert_one(vacancy_json)
            collection.replace_one({'_id': vacancy_json['_id']}, vacancy_json, True)
            return vacancy_json


