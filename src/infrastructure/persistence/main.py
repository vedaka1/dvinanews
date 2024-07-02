from typing import AsyncIterable

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from infrastructure.config import settings


def get_async_engine() -> AsyncEngine:
    return create_async_engine(settings.ASYNC_DB_URL, echo=False)


def get_sync_engine() -> Engine:
    return create_engine(settings.SYNC_DB_URL, echo=False)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


async def create_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterable[AsyncSession]:
    async with session_factory() as session:
        print(session)
        yield session
