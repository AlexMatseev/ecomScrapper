import asyncio

from core.initializer import init_models, pl_cat_scrapper, loop, set_scrapper_data, \
    pl_sub_cat_parser, pl_sub_cat_updater, pl_product_parser, pl_product_updater, run_product_scrapper, \
    get_product_scrapper, action_log

from core.scheduler import schedule_cat_parse, schedule_product_parse


def init_loop(loop):
    loop.create_task(init_models())
    action_log.info('init db models', data='')
    loop.create_task(set_scrapper_data(pl_cat_scrapper))
    loop.create_task(run_product_scrapper(pl_cat_scrapper, pl_sub_cat_parser,
                                          pl_sub_cat_updater, pl_product_parser, pl_product_updater))
    loop.create_task(schedule_cat_parse(pl_cat_scrapper))
    loop.create_task(schedule_product_parse(get_product_scrapper))


if __name__ == '__main__':
    action_log.info('Start app', data='')
    asyncio.set_event_loop(loop)
    init_loop(loop)
    loop.run_forever()
