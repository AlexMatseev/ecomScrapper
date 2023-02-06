from abc import ABCMeta, abstractmethod

import requests
from requests import ConnectTimeout
from requests.exceptions import SSLError
from sqlalchemy import select

from core import action_log
from core.session import async_session
from db.models import ParseSettings


class Parser(metaclass=ABCMeta):

    @abstractmethod
    def parse(self, html, url):
        pass

    @abstractmethod
    def get_result(self, html):
        pass


class PlCategoryParser(Parser):
    name = 'pl_parser'
    parser_type = 'html.parser'

    def __init__(self, parser):
        super(PlCategoryParser).__init__(parser)
        self.parser = parser
        self.settings = None

    def __repr__(self):
        return f'{self.__class__}, parser={self.parser}'

    def parse(self, html, url):
        action_log.info('start parsing data', data='')
        result = self.get_result(html)
        cat_names = result.findAll('a', class_=self.settings.get('CATEGORY_LIST_CLASS'))
        action_log.info('find category names from html tree', data=url)
        return {
            a.find(
                self.settings.get('CATEGORY_LINK_TAG'),
                class_=self.settings.get('CATEGORY_LINK_CLASS')).text.strip(): url + ''.join(
                a.get('href').split()
            )
            for a in cat_names if a.get('href') not in self.settings.get('EXCLUDE_URLS')
        }

    def get_result(self, html):
        return self.parser(html, self.parser_type)


class PlSubCategoryParser(PlCategoryParser):

    def __init__(self, parser):
        super(PlCategoryParser).__init__(parser)
        self.parser = parser

    def parse(self, html, url):
        if url:
            result = self.get_result(html)
            sub_cat_names = result.findAll('a', class_=self.settings.get('SUB_CATEGORY_LIST_CLASS'))
            return {
                url: {
                    a.find(self.settings.get('CATEGORY_LINK_TAG')).text.strip():
                        self.settings.get('DONOR_URL') + ''.join(a.get('href').split()) for a in sub_cat_names
                }
            }


class PlProductParser(PlCategoryParser):

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
                    data = requests.get(self.settings.get('DONOR_URL') + ''.join(page.get('href').split())).text
                    urls.append(data)
            except (ConnectTimeout, SSLError) as err:
                action_log.info('Connection loosed', data=err)
                return
            return urls

    def update_product_data(self, product_data, result, url):
        products = result.findAll('a', class_=self.settings.get('PRODUCT_LIST_CLASS'))
        for product in products:
            if '//' in product.get('href') or product.get('href') == '' \
                    or self.settings.get('URL_PATTERN_WORDS') in product.get('href'):
                continue
            name = product.find(self.settings.get('PRODUCT_LINK_TAG'), {'class': 'catalog-item__name'}).text.strip()
            price = product.find(self.settings.get('PRODUCT_LINK_TAG'), {'class': 'price__discount'})
            price = int(''.join(x for x in price.text.strip() if x.isdigit())) if price else 0

            data = {
                name: {
                    'url': self.settings.get('DONOR_URL') + ''.join(product.get('href').split()),
                    'price': price,
                    'sku': product.find(self.settings.get('PRODUCT_LINK_TAG'), {'class': 'product-code'}).text.strip(),
                }
            }
            stock = product.find(self.settings.get('PRODUCT_LINK_TAG'), {'class': 'product-status'})
            stock = self.settings.get('MIN_FAKE_STOCK') if stock else 0
            data[name]['stock'] = stock
            if name not in product_data[url].keys():
                product_data[url].update(data)
