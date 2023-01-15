import asyncio
from abc import ABCMeta, abstractmethod
from datetime import datetime

from asyncpg import UniqueViolationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core import action_log


class Updater(metaclass=ABCMeta):

    def __init__(self, session, model, parent_model=None):
        self.session = session
        self.model = model
        self.parent_model = parent_model or model

    @abstractmethod
    async def create_or_update(self, urls):
        pass

    @abstractmethod
    async def is_exist(self, model):
        pass

    @abstractmethod
    async def get_model_urls(self):
        pass


class PlCategoryUpdater(Updater):

    def __repr__(self):
        return f'{self.__class__}, model={self.model}, parent_model={self.parent_model}'

    async def is_exist(self, model):
        result = await self.session.execute(select(model))
        return result.scalars().all()

    async def create_or_update(self, urls):
        categories = await self.is_exist(self.model)
        if not categories or categories[0].created_at < datetime.now():
            async with self.session:
                action_log.info('create objects to model', data=self.model)
                objects = [
                    self.model(name=name, url=url, created_at=datetime.now())
                    for name, url in urls.items()
                ]
                self.session.add_all(objects)
                await self.session.commit()

    async def get_model_urls(self):
        check_exist = await self.is_exist(self.model)
        async with self.session:
            if not check_exist:
                while not check_exist:
                    check_exist = await self.is_exist(self.model)
                    urls = await self.session.execute(select(self.model.url))
                    await asyncio.sleep(1)
            else:
                urls = await self.session.execute(select(self.model.url))
            return urls.scalars().all()


class PlSubCategoryUpdater(PlCategoryUpdater):

    async def create_or_update(self, urls):
        sub_categories = await self.is_exist(self.model)
        if not sub_categories or sub_categories[0].created_at < datetime.now():
            async with self.session:
                action_log.info('create objects to model', data=self.model)
                objects = []
                for url in urls:
                    if isinstance(url, dict):
                        for cat_url, sub_cat in url.items():
                            objects.extend(
                                self.model(
                                    category_url=cat_url,
                                    name=name, url=url,
                                    created_at=datetime.now()) for name, url in sub_cat.items()
                            )
                self.session.add_all(objects)
                await self.session.commit()


class PlProductUpdater(PlCategoryUpdater):

    async def create_or_update(self, urls):
        products = await self.is_exist(self.model)
        if not products or products[0].created_at < datetime.now():
            async with self.session:
                action_log.info('create objects to model', data=self.model)
                for url in urls:
                    if url and isinstance(url, dict):
                        await self.add_to_db(url)
                action_log.info('Product add to database', data='')

    async def add_to_db(self, url):
        for cat_url, sub_cat in url.items():
            for name, data in sub_cat.items():
                try:
                    product = self.model(
                        sub_category_url=cat_url,
                        name=name, url=data.get('url'),
                        price=data.get('price'), sku=data.get('sku'),
                        stock=data.get('stock'),
                        created_at=datetime.now())

                    self.session.add(product)
                    await self.session.commit()
                except (IntegrityError, UniqueViolationError) as e:
                    await self.session.rollback()
