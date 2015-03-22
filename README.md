# lbcscraper
Scraper for Leboncoin.fr

## How to use

Use the generic spider:
  scrapy crawl leboncoin -a start_urls="http://www.leboncoin.fr/vetements/offres/languedoc_roussillon/herault/" -o items.js
```python
>>> import json
>>> items = json.load(open('items.json'))
>>> len(items)
726
>>> items[0]
{u'city': u'Saint-G\xe9ly-du-Fesc',
 u'link': u'http://www.leboncoin.fr/vetements/783985675.htm?ca=13_s',
 u'photo': u'http://img7.leboncoin.fr/thumbs/bf7/bf7ddfd4ad343271f95f4793add35ec5b417e354.jpg',
 u'postcode': u'34980',
 u'price': 12.0,
 u'title': u'Robe 2 en 1 taille 5 ans'}
```

Or a specialised one:
  scrapy crawl leboncoin_property -a start_urls="http://www.leboncoin.fr/ventes_immobilieres/offres/languedoc_roussillon/herault/" -o properties.json

```python
>>> import json
>>> properties = json.load(open('properties.json'))
>>> len(properties)
702
>>> properties[0]
{u'city': u'Montpellier',
 u'link': u'http://www.leboncoin.fr/ventes_immobilieres/756064558.htm?ca=13_s',
 u'photo': u'http://img3.leboncoin.fr/thumbs/a65/a65b909ca0512502149f810bbdfe1152a4e21e0c.jpg',
 u'postcode': u'34000',
 u'price': 140000.0,
 u'surface_area': 65.0,
 u'title': u'Appartement F4 65m2 proche FAC Pharmacie'}
 ```
