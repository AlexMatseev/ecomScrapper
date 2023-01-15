from abc import ABCMeta, abstractmethod

import requests
from requests import ConnectTimeout
from requests.exceptions import SSLError

from core import action_log


class Parser(metaclass=ABCMeta):

    @abstractmethod
    def parse(self, html, url):
        pass

    @abstractmethod
    def get_result(self, html):
        pass


class PlCategoryParser(Parser):
    DONOR_URL = 'https://purelogic.ru'
    CATEGORY_CLASS = 'sidebar-nav__link'
    CATEGORY_TAG = 'span'
    CATEGORY_LINK_CLASS = 'sidebar-nav-item__label'
    EXCLUDE_URLS = ['/brands/', '/uslugi/', '/catalog/sale/']
    parser_type = 'html.parser'

    def __init__(self, parser):
        super(PlCategoryParser).__init__()
        self.parser = parser

    def __repr__(self):
        return f'{self.__class__}, parser={self.parser}'

    def parse(self, html, url):
        action_log.info('start parsing data', data='')
        result = self.get_result(html)
        cat_names = result.findAll('a', class_=self.CATEGORY_CLASS)
        action_log.info('find category names from html tree', data=url)
        return {
            a.find(
                self.CATEGORY_TAG, class_=self.CATEGORY_LINK_CLASS).text.strip(): url + ''.join(
                a.get('href').split()
                )
            for a in cat_names if a.get('href') not in self.EXCLUDE_URLS
        }

    def get_result(self, html):
        return self.parser(html, self.parser_type)


class PlSubCategoryParser(PlCategoryParser):
    CATEGORY_CLASS = 'catalog-subsection__link'
    CATEGORY_TAG = 'span'

    def __init__(self, parser):
        super(PlCategoryParser).__init__(parser)
        self.parser = parser

    def parse(self, html, url):
        if url:
            result = self.get_result(html)
            sub_cat_names = result.findAll('a', class_=self.CATEGORY_CLASS)
            return {
                url: {a.find(self.CATEGORY_TAG).text.strip(): self.DONOR_URL + ''.join(a.get('href').split()) for a in
                      sub_cat_names}}


class PlProductParser(PlCategoryParser):
    PRODUCT_CLASS = 'catalog-item__link'
    PRODUCT_TAG = 'div'
    MIN_STOCK = 1
    EXCLUDE_LINK_WORDS = 'news'

    def __init__(self, parser):
        super(PlCategoryParser).__init__(parser)
        self.parser = parser

    def parse(self, html, url):
        action_log.info('start parsing product data', data='')
        result = self.get_result(html)
        product_data = {url: {}}
        if pages := self.get_page_quantity(result):
            for page in pages[1:]:
                result = self.get_result(page)
                self.update_product_data(product_data, result, url)
        return product_data

    def get_page_quantity(self, page):
        action_log.info('get page quantity', data='')
        if pages := page.findAll('a', class_='pagination-list__link'):
            urls = []
            try:
                for page in pages:
                    data = requests.get(self.DONOR_URL + ''.join(page.get('href').split())).text
                    urls.append(data)
            except (ConnectTimeout, SSLError) as err:
                action_log.info('Connection loosed', data=err)
                return
            return urls

    def update_product_data(self, product_data, result, url):
        products = result.findAll('a', class_=self.PRODUCT_CLASS)
        for product in products:
            if '//' in product.get('href') or product.get('href') == '' or self.EXCLUDE_LINK_WORDS in product.get('href'):
                continue
            name = product.find(self.PRODUCT_TAG, {'class': 'catalog-item__name'}).text.strip()
            price = product.find(self.PRODUCT_TAG, {'class': 'price__discount'})
            price = int(''.join(x for x in price.text.strip() if x.isdigit())) if price else 0

            data = {
                name: {
                    'url': self.DONOR_URL + ''.join(product.get('href').split()),
                    'price': price,
                    'sku': product.find(self.PRODUCT_TAG, {'class': 'product-code'}).text.strip(),
                }
            }
            stock = product.find(self.PRODUCT_TAG, {'class': 'product-status'})
            stock = self.MIN_STOCK if stock else 0
            data[name]['stock'] = stock
            if name not in product_data[url].keys():
                product_data[url].update(data)
