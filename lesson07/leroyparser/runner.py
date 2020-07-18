from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroyparser.spiders.leroymerlinru import LeroymerlinruSpider
from leroyparser import settings

if __name__ == '__main__':
    search = 'картины на стекле'

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    process.crawl(LeroymerlinruSpider, search=search)

    process.start()
