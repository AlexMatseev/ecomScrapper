from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker

from core import config


if config.settings.ENVIRONMENT == "PYTEST":
    sqlalchemy_database_uri = config.settings.TEST_SQLALCHEMY_DATABASE_URI
else:
    sqlalchemy_database_uri = config.settings.DB_URI


async_db_engine = create_async_engine(
    sqlalchemy_database_uri, pool_pre_ping=True, pool_size=10, max_overflow=10, pool_timeout=5
)

async_session = AsyncSession(bind=async_db_engine)  # type: ignore

if TYPE_CHECKING:
    async_session: sessionmaker[AsyncSession]  # type: ignore
