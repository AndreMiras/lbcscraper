# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from lbcscraper.items import LbcPropertyItem


class LeboncoinSpider(CrawlSpider):
    name = "leboncoin"
    allowed_domains = ["leboncoin.fr"]
    rules = (
        # follows next pages but stop at 9 to avoid crawling for too long
        Rule(LinkExtractor(allow=['\?o=\d']), callback='parse_items'),
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

    def parse_start_url(self, response):
        return self.parse_items(response)

    def parse_items(self, response):
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
            request = scrapy.Request(links[0], callback=self.parse_item_details)
            request.meta['item'] = item
            # yield item
            yield request

    def parse_item_details(self, response):
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

    def parse_item_details(self, response):
        item = super(LeboncoinPropertySpider, self).parse_item_details(response)
        surfaces_areas = response.xpath('//div[contains(@class, "criterias")]/table/tr/th[contains(text(), "Surface :")]/following-sibling::td/text()').extract()
        surfaces_areas_cleaned = [float(s.replace(" m", "").replace(" ","")) for s in surfaces_areas]
        if surfaces_areas_cleaned:
            item['surface_area'] = surfaces_areas_cleaned[0]
        ges_list = response.xpath('//div[contains(@class, "criterias")]/table/tr/th[contains(text(), "GES :")]/following-sibling::td/noscript/a/text()').extract()
        if ges_list:
            ges_match = re.search("([A-I])\s+\(de \d+ \\xe0 \d+\)", ges_list[0])
            if ges_match:
                item['ges'] = ges_match.group(1)
        energy_classes = response.xpath(u'//div[contains(@class, "criterias")]/table/tr/th[contains(text(), "Classe énergie :")]/following-sibling::td/noscript/a/text()').extract()
        if energy_classes:
            energy_class_match = re.search("([A-I])\s+\(de \d+ \\xe0 \d+\)", energy_classes[0])
            if energy_class_match:
                item['energy_class'] = energy_class_match.group(1)
        return item
