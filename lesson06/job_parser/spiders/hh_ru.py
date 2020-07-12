import scrapy
from scrapy.http import HtmlResponse
from job_parser.items import JobParserItem


class HhRuSpider(scrapy.Spider):
    name = 'hh_ru'
    allowed_domains = ['hh.ru']

    def __init__(self, vacancy=None):
        super(HhRuSpider, self).__init__()
        self.start_urls = [
            f'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text={vacancy}'
        ]

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()

        yield response.follow(next_page, callback=self.parse)

        vacansy_links = response.css('a.bloko-link.HH-LinkModifier::attr(href)').extract()

        for vacancy_link in vacansy_links:
            yield response.follow(vacancy_link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('h1::text').extract_first()

        salary = response.xpath("//span[@class='bloko-header-2 bloko-header-2_lite']/text()").extract()
        _id = response.xpath("//input[@name='vacancyId']/@value").extract_first()

        vacancy_link = response.url
        site_scraping = self.allowed_domains[0]

        yield JobParserItem(_id=_id, name=name, salary=salary, vacancy_link=vacancy_link, site_scraping=site_scraping)
