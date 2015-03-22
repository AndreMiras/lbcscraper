# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class LbcItem(Item):
    title = Field()
    link = Field()
    city = Field()
    postcode = Field()
    price = Field()
    photo = Field()
    ges = Field()
    energy_class = Field()

class LbcPropertyItem(LbcItem):
    surface_area = Field()
