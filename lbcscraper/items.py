# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class LbcItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    city = scrapy.Field()
    postcode = scrapy.Field()
    price = scrapy.Field()

class LbcPropertyItem(LbcItem):
    surface_area = scrapy.Field()
