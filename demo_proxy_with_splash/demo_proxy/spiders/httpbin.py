# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
import logging


class HttpbinSpider(scrapy.Spider):
    name = 'httpbin'

    script = '''
        function main(splash, args)
        local host = 'proxy.crawlera.com'
        local port = 8010
        local user = 'YOUR_APIKEY'
        
        splash:on_request(function(request)
            request:set_proxy{host, port, username=user, password=''}  
        end)
        
        assert(splash:go(args.url))
        assert(splash:wait(0.5))
        return splash:html()
        end


    '''

    def start_requests(self):
        for i in range(1, 11):
            yield SplashRequest(url='https://httpbin.org/ip', callback=self.parse, dont_filter=True, endpoint='execute', args={'wait': 1.0, 'lua_source': self.script})

    def parse(self, response):
        logging.info(response.body)
