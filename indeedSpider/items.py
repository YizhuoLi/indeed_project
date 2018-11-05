# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IndeedspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class IndeedItem(scrapy.Item):
    job_title = scrapy.Field()
    company_name = scrapy.Field()
    job_location = scrapy.Field()
    job_summary = scrapy.Field()
    job_salary = scrapy.Field()
    job_href = scrapy.Field()
    job_star = scrapy.Field()
    job_review = scrapy.Field()