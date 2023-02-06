import asyncio

from core.initializer import loop, action_log, init_data


def main(loop):
    loop.create_task(init_data())
    action_log.info('init data', data='')


if __name__ == '__main__':
    action_log.info('Start app', data='')
    asyncio.set_event_loop(loop)
    main(loop)
    loop.run_forever()
