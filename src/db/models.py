from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import backref, declarative_base
from sqlalchemy.orm import relationship

BaseModel = declarative_base()


class Category(BaseModel):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'Category(id={self.id!r}, name={self.name!r}, url={self.url!r})'


class SubCategory(BaseModel):
    __tablename__ = 'sub_category'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    category_url = Column(String, ForeignKey('category.url'))
    sub_category = relationship(
        'Category', backref=backref('sub_categories', lazy='dynamic'))

    def __repr__(self):
        return f'SubCategory(id={self.id!r}, name={self.name!r})'


class Product(BaseModel):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    sku = Column(String)
    stock = Column(Integer)
    url = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    sub_category_url = Column(String, ForeignKey('sub_category.url'))
    category = relationship(
        'SubCategory', backref=backref('cat_products', lazy='dynamic'))

    def __repr__(self):
        return f'Product(id={self.id!r}, name={self.name!r})'

# class Address(Base):
#     __tablename__ = "address"
#
#     id = Column(Integer, primary_key=True)
#     email_address = Column(String, nullable=False)
#     user_id = Column(Integer, ForeignKey("user_account.id"), nullable=False)
#
#     user = relationship("User", back_populates="addresses")
#
#     def __repr__(self):
#         return f"Address(id={self.id!r}, email_address={self.email_address!r})"
