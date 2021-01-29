# -*- coding: utf-8 -*-
import scrapy
import json
import os
import datefinder
import lxml.html.clean
import argparse
from w3lib.http import basic_auth_header
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging


def date_fetch(date):
    try:
        if date:
            for gr in ['Updated:', 'Modified:']:
                date = date.replace(gr, ' ')
            matches = datefinder.find_dates(date)
            *_, last = matches
            date = last.strftime("%Y-%m-%d %H:%M:%S")
        else:
            date = 'None'
    except:
        date = 'None'
    return date

class CrawlDataSpider(CrawlSpider):
    name = 'crawl_data'
    # custom_settings = { 'DEPTH_PRIORITY' : 1, 'SCHEDULER_DISK_QUEUE' : 'scrapy.squeues.PickleFifoDiskQueue', 'SCHEDULER_MEMORY_QUEUE' : 'scrapy.squeues.FifoMemoryQueue', 'FEED_FORMAT' : 'csv',
    #                     'FEED_URI' : 'toi_articles.csv', 'LOG_FILE': 'log.txt'}
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    # rules = (
    #     Rule(LinkExtractor(allow=r'(.*timesofindia.indiatimes)(.*/articleshow/)'), callback='parse_item', follow=True, process_request='set_user_agent'),
    # )
    rules = (
        Rule(LinkExtractor(allow=r'(.*indiatoday.in)(.*/story/)'), callback='parse_item', follow=True, process_request='set_user_agent'),
    )
    # allowed_domains = []
    def __init__(self, depth, site_name, config = None):
        super().__init__()
        self.site_name = site_name
        self.depth = int(depth)
        with open(config, 'r') as f:
            self.config = json.load(f)
            self.config = self.config.get(site_name)
        self.allowed_domains = self.config.get("allowed_domains")

        

        
    def set_user_agent(self, request, response):
        # request.meta['proxy'] = "https://proxy.tcs.com:8080"
        # request.headers['Proxy-Authorization'] = basic_auth_header('1706872', 'India@06')
        request.headers['User-Agent'] = self.user_agent
        return request

    def start_requests(self):
        yield scrapy.Request(url=self.config.get('url'), headers={
            'User-Agent': self.user_agent
        })
    
    def parse_item(self, response):
        res = Selector(text = lxml.html.clean.clean_html(response.body)) 
        parse_details = self.config.get("parse")
        mandatory_fields = self.config.get("mandatory")
        mandatory_fields_present = True
        item = {}
        item["url"] = response.url
        for k,v in parse_details.items():
            item[k] = "".join(response.xpath(v).extract())
        
        item['date'] = date_fetch("".join(response.xpath(parse_details.get('date')).extract()))

        if len(mandatory_fields) != 0:
            for field in mandatory_fields:
                if not item[field]:
                    mandatory_fields_present = False

        if mandatory_fields_present:
            yield item
        else:
            pass
    
#[RequestID, Keyword, Url, Source, StartDate, Headline, filepath, filetype, filename, EndDate, ]
    
parser = argparse.ArgumentParser()
parser.add_argument('-w', '--website', help = 'Website list to be selected')
parser.add_argument('-sectionA', '--sectionAvoid',help = 'List Of Section To be avoided PIPE seperated as sting without space',default='')
parser.add_argument('-sectionI', '--sectionInclude',help = 'List Of Section To be included PIPE seperated as sting without space',default='')
parser.add_argument('-ct', '--websiteConfig',help='website sttructure configuration')
# parser.add_argument('-o','--outputPath',help='path of output')
parser.add_argument('-d','--depth',help='depth of website crawling')
parser.add_argument('-r','--requestID',help='depth of website crawling')
parser.add_argument('-k','--keywords',help='List of keywords To be included in the article, PIPE separated as string without space', default = '')
args = parser.parse_args()

#*********************************************Argument Parser Section*********************************************

depth = int(args.depth)
site_name = args.website
config = args.websiteConfig
requestID = args.requestID

#*********************************************Get Spider Settings and Update Settings*********************************************

configure_logging()
settings = get_project_settings()
custom_settings = { 'DEPTH_LIMIT': depth ,'DEPTH_PRIORITY' : 1, 'SCHEDULER_DISK_QUEUE' : 'scrapy.squeues.PickleFifoDiskQueue', 'SCHEDULER_MEMORY_QUEUE' : 'scrapy.squeues.FifoMemoryQueue', 'FEED_FORMAT' : 'csv',
                        'FEED_URI' : 'india_today_articles.csv', 'LOG_FILE': 'india_log.txt'}
settings.update(custom_settings)

#*********************************************Run Spider Using Process Crawler*********************************************

# process = CrawlerProcess(settings)
# process.crawl(CrawlDataSpider, depth = depth, site_name = site_name, config = config)
# process.start()

#*********************************************Run Spider Using Crawler Runner*********************************************

runner = CrawlerRunner(custom_settings)
runner.crawl(CrawlDataSpider, depth = depth, site_name = site_name, config = config)
d = runner.join()
d.addBoth(lambda _: reactor.stop())
reactor.run() 
        
