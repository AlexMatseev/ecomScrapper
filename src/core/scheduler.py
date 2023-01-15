import asyncio

import aioschedule

from core import action_log
from core.config import CATEGORY_UPDATE_PERIOD, CATEGORY_JOB_TIME, PRODUCT_JOB_TIME
from core.initializer import pl_cat_scrapper, pl_sub_cat_parser, pl_sub_cat_updater, pl_product_parser, \
    pl_product_updater


async def schedule_cat_parse(cat_scrapper):
    aioschedule.every(CATEGORY_UPDATE_PERIOD).days.at(CATEGORY_JOB_TIME).do(cat_scrapper.parse_urls)
    action_log.info('start schedule update category data', data='')
    while True:
        await asyncio.sleep(.1)
        await aioschedule.run_pending()


async def schedule_product_parse(get_product_scrapper):
    product_scrapper = await get_product_scrapper(pl_cat_scrapper, pl_sub_cat_parser,
                                                  pl_sub_cat_updater, pl_product_parser, pl_product_updater)

    aioschedule.every().day.at(PRODUCT_JOB_TIME).do(product_scrapper.parse_urls)
    action_log.info('start schedule update products data', data='')
    while True:
        await asyncio.sleep(.1)
        await aioschedule.run_pending()

