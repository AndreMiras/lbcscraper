#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = 'lbcscraper',
    version = '1.0',
    description='Scraper for Leboncoin.fr',
    author='Andre Miras',
    url='https://github.com/AndreMiras/lbcscraper',
    packages = find_packages(),
    entry_points = {
        'scrapy': ['settings = lbcscraper.settings']
    },
    install_requires=['scrapy'],
)
