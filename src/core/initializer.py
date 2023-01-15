import asyncio
import concurrent

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core import action_log
from core.config import DB_URL, DONOR_URL
from db.models import Category, SubCategory, Product, BaseModel
from parse import PlCategoryParserCreater, PlSubCategoryParserCreater, PlProductParserCreater
from parse.scrappers import PlScrapper

parser = BeautifulSoup
_pool = concurrent.futures.ProcessPoolExecutor()

db_engine = create_async_engine(
    DB_URL,
    pool_size=10,
    max_overflow=10,
    pool_timeout=5
)

session = AsyncSession(bind=db_engine)
loop = asyncio.new_event_loop()

pl_cat_parser = PlCategoryParserCreater.create_parser(BeautifulSoup)
pl_cat_updater = PlCategoryParserCreater.create_updater(session, Category)
pl_sub_cat_parser = PlSubCategoryParserCreater.create_parser(BeautifulSoup)
pl_sub_cat_updater = PlSubCategoryParserCreater.create_updater(session, SubCategory, Category)
pl_product_parser = PlProductParserCreater.create_parser(BeautifulSoup)
pl_product_updater = PlProductParserCreater.create_updater(session, Product, SubCategory)

pl_cat_scrapper = PlScrapper(DONOR_URL, pl_cat_parser, pl_cat_updater, loop)


async def init_models():
    async with db_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)


async def get_scrapper(parent_scrapper, parser, updater, loop):
    urls = await parent_scrapper.updater.get_model_urls()
    return PlScrapper(urls, parser, updater, loop)


async def set_scrapper_data(category_scrapper):
    await category_scrapper.parse_urls()
    action_log.info('update Category database model', data=category_scrapper)


async def run_product_scrapper(scraper, parent_parser, parent_updater, parser, updater, loop=loop):
    parent_scrapper = await get_scrapper(scraper, parent_parser, parent_updater, loop)
    await parent_scrapper.parse_urls()
    scrapper = await get_scrapper(parent_scrapper, parser, updater, loop)
    await scrapper.parse_urls()
    return scrapper


async def get_product_scrapper(scraper, parent_parser, parent_updater, parser, updater, loop=loop):
    parent_scrapper = await get_scrapper(scraper, parent_parser, parent_updater, loop)
    return await get_scrapper(parent_scrapper, parser, updater, loop)
