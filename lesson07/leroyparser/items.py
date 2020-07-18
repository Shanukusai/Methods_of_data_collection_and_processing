# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
import re

# def cleaner_photo(value):
#     if value[:2] == '//':
#         return f'http:{value}'
#     else:
#         return value


def to_int(value):
    return int(value.replace(' ', ''))


def clear_spaces(value):
    value = re.sub("^\s+|\s+$", "", value, flags=re.UNICODE)
    value = " ".join(re.split("\s+", value, flags=re.UNICODE))
    return value


class LeroyparserItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    # photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    specifications_key = scrapy.Field()
    specifications_value = scrapy.Field(input_processor=MapCompose(clear_spaces))
    specifications = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(to_int), output_processor=TakeFirst())
    pass
