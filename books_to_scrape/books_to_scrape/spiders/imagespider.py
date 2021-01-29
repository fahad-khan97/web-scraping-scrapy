import scrapy
from scrapy.loader import ItemLoader
from books_to_scrape.items import BooksToScrapeItem


class ImageSpider(scrapy.Spider):
    name = 'downloader'

    start_urls = ['http://books.toscrape.com']

    def parse(self, response):
        for article in response.xpath("//article[@class='product_pod']"):
            loader = ItemLoader(item=BooksToScrapeItem(), selector=article)
            relative_url = article.xpath(".//div[@class='image_container']/a/img/@src").extract_first()
            absolute_url = response.urljoin(relative_url)
            loader.add_value('image_urls', absolute_url)
            loader.add_xpath('book_name', ".//h3/a/@title")
            yield loader.load_item()