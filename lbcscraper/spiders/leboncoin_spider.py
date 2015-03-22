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
        Retrieves start_urls from command line options:
        scrapy crawl leboncoin -a start_urls="http://www.leboncoin.fr/vetements/offres/languedoc_roussillon/herault/,http://www.leboncoin.fr/vetements/offres/languedoc_roussillon/herault/"
        """
        super(LeboncoinSpider, self).__init__(*args, **kwargs) 
        start_urls = kwargs.get('start_urls')
        self.start_urls = start_urls and start_urls.split(',') or []

    def custom_start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        ads_elems = response.xpath('//div[@class="list-lbc"]/a')
        for ad_elem in ads_elems:
            item = LbcPropertyItem()
            links = ad_elem.xpath('@href').extract()
            item['link'] = links[0]
            details_elem = ad_elem.xpath('div[@class="lbc"]/div[@class="detail"]')
            titles = details_elem.xpath('div[@class="title"]/text()').extract()
            titles_cleaned = [s.strip() for s in titles]
            item['title'] = titles_cleaned[0]
            prices = details_elem.xpath('div[@class="price"]/text()').extract()
            prices_cleaned = [float(s.replace(u"\xa0€", "").replace(" ", "").strip()) for s in prices]
            if prices_cleaned:
                item['price'] = prices_cleaned[0]
            photos = ad_elem.xpath('div[@class="lbc"]/div[@class="image"]/div[@class="image-and-nb"]/img/@src').extract()
            if photos:
                item['photo'] = photos[0]
            request = scrapy.Request(links[0], callback=self.parse_details)
            request.meta['item'] = item
            # yield item
            yield request

    def parse_details(self, response):
        item = response.meta['item']
        cities = response.xpath('//table/tr/th[contains(text(), "Ville :")]/following-sibling::td/text()').extract()
        if cities:
            item['city'] = cities[0]
        postcodes = response.xpath('//table/tr/th[contains(text(), "Code postal :")]/following-sibling::td/text()').extract()
        if postcodes:
            item['postcode'] = postcodes[0]
        # yield item
        return item

class LeboncoinPropertySpider(LeboncoinSpider):
    """
    scrapy crawl leboncoin_property -a start_urls="http://www.leboncoin.fr/ventes_immobilieres/offres/languedoc_roussillon/herault/"
    """
    name = "leboncoin_property"

    def parse_details(self, response):
        item = super(LeboncoinPropertySpider, self).parse_details(response)
        surfaces_areas = response.xpath('//div[contains(@class, "criterias")]/table/tr/th[contains(text(), "Surface :")]/following-sibling::td/text()').extract()
        surfaces_areas_cleaned = [float(s.replace(" m", "")) for s in surfaces_areas]
        if surfaces_areas_cleaned:
            item['surface_area'] = surfaces_areas_cleaned[0]
        return item
