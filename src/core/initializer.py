import asyncio
import concurrent
import os

import yaml
from bs4 import BeautifulSoup
from sqlalchemy import select

from core import action_log
from core.config import PROJECT_DIR
from core.scheduler import schedule_cat_parse, schedule_product_parse
from core.session import async_session, async_db_engine
from db.models import Category, SubCategory, Product, BaseModel, ParseSettings
from parse import PlCategoryParserCreater, PlSubCategoryParserCreater, PlProductParserCreater
from parse.scrappers import PlScrapper

parser = BeautifulSoup
_pool = concurrent.futures.ProcessPoolExecutor()

loop = asyncio.new_event_loop()

pl_cat_parser = PlCategoryParserCreater.create_parser(BeautifulSoup)
pl_cat_updater = PlCategoryParserCreater.create_updater(async_session, Category)
pl_sub_cat_parser = PlSubCategoryParserCreater.create_parser(BeautifulSoup)
pl_sub_cat_updater = PlSubCategoryParserCreater.create_updater(async_session, SubCategory, Category)
pl_product_parser = PlProductParserCreater.create_parser(BeautifulSoup)
pl_product_updater = PlProductParserCreater.create_updater(async_session, Product, SubCategory)

pl_cat_scrapper = PlScrapper(pl_cat_parser, pl_cat_updater, loop)


async def set_parse_settings(tool, session):
    statement = select(ParseSettings).where(ParseSettings.name == tool.name)
    settings = await async_session.execute(statement)
    if settings := settings.scalars().first():
        tool.settings = settings.data


async def get_scrapper(parent_scrapper, parser, updater, loop):
    urls = await parent_scrapper.updater.get_model_urls()
    return PlScrapper(parser, updater, loop, urls)


async def set_scrapper_data(category_scrapper, session):
    statement = select(ParseSettings).where(ParseSettings.name == category_scrapper.name)
    settings = await session.execute(statement)
    if settings := settings.scalars().first():
        category_scrapper.donor_urls = settings.data.get('DONOR_URL')
        await category_scrapper.parse_urls()
        action_log.info('update Category database model', data=category_scrapper)


async def run_product_scrapper(scraper, parent_parser, parent_updater, parser, updater, loop=loop):
    parent_scrapper = await get_scrapper(scraper, parent_parser, parent_updater, loop)
    await parent_scrapper.parse_urls()
    scrapper = await get_scrapper(parent_scrapper, parser, updater, loop)
    await scrapper.parse_urls()


async def get_product_scrapper(scraper, parent_parser, parent_updater, parser, updater, loop=loop):
    parent_scrapper = await get_scrapper(scraper, parent_parser, parent_updater, loop)
    return await get_scrapper(parent_scrapper, parser, updater, loop)


async def init_tasks(cat_scrapper, product_scrapper, session):
    statement = select(ParseSettings).where(ParseSettings.name == 'tasks')
    result = await session.execute(statement)
    settings = result.scalars().first()
    await schedule_cat_parse(cat_scrapper, settings.data)
    await schedule_product_parse(product_scrapper, settings.data)



async def init_data():
    async with async_session as session:
        result = await session.execute(select(ParseSettings))
        if not result.scalars().all():
            path = os.path.join(PROJECT_DIR, 'parse_settings.yaml')
            with open(path, 'r') as file:
                settings = yaml.load(file, yaml.FullLoader)
                objects = [ParseSettings(name=setting.get('name'), data=setting.get('data')) for setting in settings]
            session.add_all(objects)
            await session.commit()
        await set_parse_settings(pl_cat_parser, session)
        await set_parse_settings(pl_sub_cat_parser, session)
        await set_parse_settings(pl_product_parser, session)
        await set_scrapper_data(pl_cat_scrapper, session)
        await run_product_scrapper(pl_cat_scrapper, pl_sub_cat_parser,
                                      pl_sub_cat_updater, pl_product_parser, pl_product_updater)
        await init_tasks(pl_cat_scrapper, get_product_scrapper, session)
