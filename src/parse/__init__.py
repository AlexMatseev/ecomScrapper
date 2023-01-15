from abc import ABCMeta, abstractmethod
from parse.db_updater import PlCategoryUpdater, PlSubCategoryUpdater, PlProductUpdater
from parse.parsers import PlCategoryParser, PlSubCategoryParser, PlProductParser


class BaseParser(metaclass=ABCMeta):
    """
    Объявление интерфейса для методов, которые создают объекты.
    """

    @abstractmethod
    def create_parser(self, parse):
        pass

    @abstractmethod
    def create_updater(self, session, model, parent_model):
        pass


class PlCategoryParserCreater(BaseParser):
    @classmethod
    def create_parser(cls, parser):
        """Метод создания окна, возврашает класс окно"""
        return PlCategoryParser(parser)

    @classmethod
    def create_updater(cls, session, model, parent_model=None):
        """Метод создания кнопки, возврашает класс кнопки"""
        return PlCategoryUpdater(session, model, parent_model)


class PlSubCategoryParserCreater(BaseParser):
    @classmethod
    def create_parser(cls, parse):
        """Метод создания окна, возврашает класс окно"""
        return PlSubCategoryParser(parse)

    @classmethod
    def create_updater(cls, session, model, parent_model):
        """Метод создания кнопки, возврашает класс кнопки"""
        return PlSubCategoryUpdater(session, model, parent_model)


class PlProductParserCreater(BaseParser):
    @classmethod
    def create_parser(cls, parse):
        """Метод создания окна, возврашает класс окно"""
        return PlProductParser(parse)

    @classmethod
    def create_updater(cls, session, model, parent_model):
        """Метод создания кнопки, возврашает класс кнопки"""
        return PlProductUpdater(session, model, parent_model)
