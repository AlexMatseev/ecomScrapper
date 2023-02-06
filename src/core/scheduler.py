import asyncio
import aioschedule

from core import action_log


async def schedule_cat_parse(cat_scrapper, task_settings):
    aioschedule.every(
        task_settings.get('CATEGORY_UPDATE_PERIOD')
    ).days.at(task_settings.get('CATEGORY_JOB_TIME')).do(cat_scrapper.parse_urls)

    action_log.info('start schedule update category data', data='')
    while True:
        await asyncio.sleep(.1)
        await aioschedule.run_pending()


async def schedule_product_parse(product_scrapper, task_settings):

    aioschedule.every().day.at(task_settings.get('PRODUCT_JOB_TIME')).do(product_scrapper.parse_urls)
    action_log.info('start schedule update products data', data='')
    while True:
        await asyncio.sleep(.1)
        await aioschedule.run_pending()
