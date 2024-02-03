import logging
from typing import AsyncGenerator

import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import settings

engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()


async def get_redis() -> AsyncGenerator:
    try:
        logging.warning('Getting redis session...')
        redis = aioredis.ConnectionPool.from_url(
            'redis://redis:6379', decode_responses=True
        )
        logging.warning('Redis connection pool initialized successfully :)')
        yield redis
    finally:
        logging.warning('Could not initialize connection pool to redis!')