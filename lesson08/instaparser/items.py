# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_id = scrapy.Field()
    subscriber_status = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    photo = scrapy.Field()
    full_info = scrapy.Field()

