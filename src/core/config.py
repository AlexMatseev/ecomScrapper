# PARSER

DONOR_URL = 'https://purelogic.ru'
CATEGORY_LIST_CLASS = 'sidebar-nav__link'
CATEGORY_LINK_TAG = 'span'
EXCLUDE_URLS = ['/brands/', '/uslugi/', '/catalog/sale/']
CATEGORY_LINK_CLASS = 'sidebar-nav-item__label'
SUB_CATEGORY_LIST_CLASS = 'catalog-subsection__link'
PRODUCT_LIST_CLASS = 'catalog-item__link'
PRODUCT_LINK_TAG = 'div'
PRODUCT_FIND_NAME = {'class': 'catalog-item__name'}
MIN_FAKE_STOCK = 1
PLG_PAGEN_URL_PATTERN = f'{DONOR_URL}/filter/clear/apply/?PAGEN_1='
URL_PATTERN_WORDS = 'news'

# TASKS
CATEGORY_UPDATE_PERIOD = 30
CATEGORY_JOB_TIME = '8:22'
PRODUCT_JOB_TIME = '3:00'

# DATABASE
HOST = '127.0.0.1'
USER = 'postgres'
PASSWORD = 'postgres'
DB_NAME = 'actual_product'
DB_URL = f'postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}/{DB_NAME}'
