# -*- coding: utf-8 -*-
import re
import scrapy
from urlparse import urlparse
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

    @staticmethod
    def add_scheme_if_missing(url):
        """
        Adds the http:// scheme if missing in the URL.
        >>> url = 'www.leboncoin.fr/'
        >>> LeboncoinSpider.add_scheme_if_missing(url)
        'http://www.leboncoin.fr/'
        >>> url = '//www.leboncoin.fr/'
        >>> LeboncoinSpider.add_scheme_if_missing(url)
        'http://www.leboncoin.fr/'
        >>> url = 'http://www.leboncoin.fr/'
        >>> LeboncoinSpider.add_scheme_if_missing(url)
        'http://www.leboncoin.fr/'
        """
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            # the '//' could or couldn't be omitted
            if not url.startswith('//'):
                url = '//' + url
            url = 'http:' + url
        return url

    def parse_items(self, response):
        # selects the middle ads list, but not the right side ads
        ads_elems = response.xpath('//ul/li/a[contains(@class, "list_item")]')
        for ad_elem in ads_elems:
            item = LbcPropertyItem()
            links = ad_elem.xpath('@href').extract()
            link = links[0]
            link = LeboncoinSpider.add_scheme_if_missing(link)
            item['link'] = link
            details_elem = ad_elem.xpath('section[@class="item_infos"]')
            titles = details_elem.xpath('h2[@class="item_title"]/text()').extract()
            titles_cleaned = [s.strip() for s in titles]
            item['title'] = titles_cleaned[0]
            prices = details_elem.xpath('h3[@class="item_price"]/text()').extract()
            prices_cleaned = [float(s.replace(u"\xa0€", "").replace(" ", "").strip()) for s in prices]
            if prices_cleaned:
                item['price'] = prices_cleaned[0]
            photos = ad_elem.xpath('div[@class="item_image"]/span[@class="item_imagePic"]/span/@data-imgsrc').extract()
            if photos:
                photo = LeboncoinSpider.add_scheme_if_missing(photos[0])
                item['photo'] = photo
            request = scrapy.Request(link, callback=self.parse_item_details)
            request.meta['item'] = item
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
        properties_elem = response.xpath('//section[contains(@class, "properties")]')
        surfaces_areas = properties_elem.xpath('div/h2/span[contains(text(), "Surface")]/following-sibling::span/text()').extract()
        surfaces_areas_cleaned = [float(s.replace(" m", "").replace(" ","")) for s in surfaces_areas]
        if surfaces_areas_cleaned:
            item['surface_area'] = surfaces_areas_cleaned[0]
        ges_list = properties_elem.xpath('div/h2/span[contains(text(), "GES")]/following-sibling::span/a/text()').extract()
        if ges_list:
            ges_match = re.search("([A-I])\s+\(de \d+ \\xe0 \d+\)", ges_list[0])
            if ges_match:
                item['ges'] = ges_match.group(1)
        energy_classes = properties_elem.xpath(u'div/h2/span[contains(text(), "Classe énergie")]/following-sibling::span/a/text()').extract()
        if energy_classes:
            energy_class_match = re.search("([A-I])\s+\(de \d+ \\xe0 \d+\)", energy_classes[0])
            if energy_class_match:
                item['energy_class'] = energy_class_match.group(1)
        return item
