import scrapy
from scrapy.http import HtmlResponse
from job_parser.items import JobParserItem


class SuperjobRuSpider(scrapy.Spider):
    name = 'superjob_ru'
    allowed_domains = ['superjob.ru']

    def __init__(self, vacancy=None):
        super(SuperjobRuSpider, self).__init__()
        self.start_urls = [
            f'https://www.superjob.ru/vacancy/search/?keywords={vacancy}'
        ]

    def parse(self, response):
        next_page = response.css('a.f-test-button-dalshe::attr(href)').extract_first()

        yield response.follow(next_page, callback=self.parse)

        vacansy_links = response.css(
            'a[class*=f-test-link][href^="/vakansii"]::attr(href)'
        ).extract()

        for vacancy_link in vacansy_links:
            yield response.follow(vacancy_link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('h1 ::text').extract()

        salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()

        _id = response.xpath("//div/div[@class='_2g1F-']/span[@class='_3mfro _9fXTd _2JVkc _2VHxz']/text()").extract()

        vacancy_link = response.url

        site_scraping = self.allowed_domains[0]

        yield JobParserItem(
            _id=_id, \
            name=name, \
            salary=salary, \
            vacancy_link=vacancy_link, \
            site_scraping=site_scraping
        )
