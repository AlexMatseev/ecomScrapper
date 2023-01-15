import asyncio
import concurrent
import contextlib
from abc import ABCMeta, abstractmethod

import aiohttp
from aiohttp import ClientConnectorError

from core import action_log


class Scrapper(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    async def parse_urls(self):
        """Create tasks to parse from donor url and call update func"""

    @abstractmethod
    async def fetch_and_parse(self, session, url):
        """Get response data and call parse func"""

    @abstractmethod
    async def fetch(self, session, url):
        """Make request to donor url and return response data"""


class PlScrapper(Scrapper):

    def __init__(self, urls, parser, updater, loop):
        self.donor_urls = urls
        self.parser = parser
        self.updater = updater
        self.loop = loop
        self._pool = concurrent.futures.ProcessPoolExecutor()

    def __repr__(self):
        return f'{self.__class__}, parser_tool={self.parser}, updater_tool={self.updater}'

    async def parse_urls(self):
        async with aiohttp.ClientSession() as session:
            if isinstance(self.donor_urls, list):
                tasks = [self.fetch_and_parse(session, url) for url in self.donor_urls]
                res = await asyncio.gather(*tasks)
                await self.updater.create_or_update(res)
            else:
                action_log.info('prepare to get data from url', data=self.donor_urls)
                res = await asyncio.gather(self.fetch_and_parse(session, self.donor_urls))
            await self.updater.create_or_update(res[0])

    async def fetch_and_parse(self, session, url):
        html = await self.fetch(session, url)
        action_log.info('get html tree from url', data=url)
        if html:
            return await self.loop.run_in_executor(self._pool, self.parser.parse, html, url)

    async def fetch(self, session, url):
        with contextlib.suppress(ClientConnectorError):
            async with session.get(url) as resp:
                return await resp.text()
