import scrapy
from scrapy.http import HtmlResponse
from leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response):
        product_links = response.xpath("//a[@class='black-link product-name-inner']")
        for link in product_links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_xpath('_id', "//uc-pdp-card-ga-enriched[@class='card-data']/@data-product-id")
        loader.add_xpath('name', "//h1[@class='header-2']/text()")
        loader.add_xpath('photos', "//picture[@slot='pictures']/img/@src")
        loader.add_xpath('specifications_key', "//div[@class='def-list__group']/dt/text()")
        loader.add_xpath('specifications_value', "//div[@class='def-list__group']/dd/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('price', "//span[@slot='price']/text()")
        yield loader.load_item()




