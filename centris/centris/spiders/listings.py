# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
import json


class ListingsSpider(scrapy.Spider):
    name = 'listings'
    allowed_domains = ['www.centris.ca']

    http_user = 'user'
    http_pass = 'userpass'

    position = {
        "startPosition": 0
    }

    script = '''
        function main(splash, args)
            splash:on_request(function(request)
                if request.url:find('css') then
                    request.abort()
                end
            end)
            splash.images_enabled = false
            splash.js_enabled = false
            assert(splash:go(args.url))
            assert(splash:wait(0.5))
            return splash:html()
        end
    '''

    def start_requests(self):
        query = {
            "queryView": {
                "Filters": [
                    {
                        "MatchType": "CityDistrictAll",
                        "Text": "Montréal (All boroughs)",
                        "Id": "5"
                    }
                ],
                "FieldsValues": [
                    {
                        "fieldId": "CityDistrictAll",
                        "value": "5"
                    },
                    {
                        "fieldId": "Category",
                        "value": "Residential"
                    },
                    {
                        "fieldId": "SellingType",
                        "value": "Rent"
                    },
                    {
                        "fieldId": "LandArea",
                        "value": "SquareFeet"
                    },
                    {
                        "fieldId": "RentPrice",
                        "value": 0
                    },
                    {
                        "fieldId": "RentPrice",
                        "value": 1500
                    }
                ]
            },
            "isHomePage": True
        }
        yield scrapy.Request(
            url="https://www.centris.ca/mvc/property/UpdateQuery",
            method="POST",
            body=json.dumps(query),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.update_query
        )

    def update_query(self, response):
        yield scrapy.Request(
            url="https://www.centris.ca/Mvc/Property/GetInscriptions",
            method="POST",
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.parse
        )

    def parse(self, response):
        resp_dict = json.loads(response.body)
        html = resp_dict.get('d').get('Result').get('html')
        sel = Selector(text=html)
        listings = sel.xpath("//div[@class='row templateListItem']")
        for listing in listings:
            category = listing.xpath(
                ".//div[@class='description']/h2/span/text()").get()
            features = listing.xpath(
                ".//div[@class='description']/p[@class='features border']/span/span/text()").get()
            price = listing.xpath(
                ".//div[@class='description']/p[@class='price']/span/text()").get()
            city = listing.xpath(
                ".//div[@class='description']/p[@class='address']/span/text()").get()
            url = listing.xpath(".//a[@class='btn a-more-detail']/@href").get()
            abs_url = f"https://www.centris.ca{url}"

            yield SplashRequest(
                url=abs_url,
                endpoint='execute',
                callback=self.parse_summary,
                args={
                    'lua_source': self.script
                },
                meta={
                    'cat': category,
                    'fea': features,
                    'pri': price,
                    'city': city,
                    'url': abs_url
                }
            )

        count = resp_dict.get('d').get('Result').get('count')
        increment_number = resp_dict.get('d').get(
            'Result').get('inscNumberPerPage')

        if self.position['startPosition'] <= count:
            self.position['startPosition'] += increment_number
            yield scrapy.Request(
                url="https://www.centris.ca/Mvc/Property/GetInscriptions",
                method="POST",
                body=json.dumps(self.position),
                headers={
                    'Content-Type': 'application/json'
                },
                callback=self.parse
            )

    def parse_summary(self, response):
        address = response.xpath("//h2[@itemprop='address']/text()").get()
        description = response.xpath(
            "normalize-space(//div[@itemprop='description']/text())").get()
        category = response.request.meta['cat']
        features = response.request.meta['fea']
        price = response.request.meta['pri']
        city = response.request.meta['city']
        url = response.request.meta['url']

        yield {
            'address': address,
            'category': category,
            'description': description,
            'features': features,
            'price': price,
            'city': city,
            'url': url
        }
