# -*- coding: utf-8 -*-
import scrapy
from lbcscraper.items import LbcPropertyItem


class LeboncoinSpider(scrapy.Spider):
    name = "leboncoin"
    allowed_domains = ["leboncoin.fr"]
    start_urls = (
        # 'http://www.leboncoin.fr/',
        # 'http://www.leboncoin.fr/ventes_immobilieres/offres/languedoc_roussillon/herault/',
    )

    def __init__(self, *args, **kwargs): 
        """
        Retrieves start_url from command line options:
        scrapy crawl leboncoin -a start_url="http://www.leboncoin.fr/vetements/offres/languedoc_roussillon/herault/"
        """
        super(LeboncoinSpider, self).__init__(*args, **kwargs) 
        self.start_urls = [kwargs.get('start_url')] 

    def custom_start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        ads_elems = response.xpath('//div[@class="list-lbc"]/a')
        for ad_elem in ads_elems:
            item = LbcPropertyItem()
            link = ad_elem.xpath('@href').extract()
            item['link'] = link
            details_elem = ad_elem.xpath('div[@class="lbc"]/div[@class="detail"]')
            title = details_elem.xpath('div[@class="title"]/text()').extract()
            item['title'] = [s.strip() for s in title]
            price = details_elem.xpath('div[@class="price"]/text()').extract()
            item['price'] = [s.replace(u"\xa0€", "").replace(" ", "").strip() for s in price]
            request = scrapy.Request(link[0], callback=self.parse_details)
            request.meta['item'] = item
            # yield item
            yield request

    def parse_details(self, response):
        item = response.meta['item']
        city = response.xpath('//table/tr/th[contains(text(), "Ville :")]/following-sibling::td/text()').extract()
        item['city'] = city
        postcode = response.xpath('//table/tr/th[contains(text(), "Code postal :")]/following-sibling::td/text()').extract()
        item['postcode'] = postcode
        # yield item
        return item

class LeboncoinPropertySpider(LeboncoinSpider):
    """
    scrapy crawl leboncoin_property -a start_url="http://www.leboncoin.fr/ventes_immobilieres/offres/languedoc_roussillon/herault/"
    """
    name = "leboncoin_property"

    def parse_details(self, response):
        item = super(LeboncoinPropertySpider, self).parse_details(response)
        surface_area = response.xpath('//div[contains(@class, "criterias")]/table/tr/th[contains(text(), "Surface :")]/following-sibling::td/text()').extract()
        item['surface_area'] = [s.replace(" m", "") for s in surface_area]
        return item
