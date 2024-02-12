from typing import AsyncGenerator

import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import settings

engine = create_async_engine(
    settings.REAL_DATABASE_URL,
    future=True, echo=True
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncGenerator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()


def create_redis() -> aioredis.ConnectionPool:
    return aioredis.ConnectionPool.from_url(
        'redis://redis:6379',
        decode_responses=True
    )


redis_pool = create_redis()


def get_redis() -> aioredis.Redis:
    return aioredis.Redis(connection_pool=redis_pool)
