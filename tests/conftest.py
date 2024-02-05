import asyncio
import logging
import sys
from typing import Any, AsyncGenerator

import aioredis
import asyncpg
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

import settings
from app.db.session import get_db
from main import app

sys.path.append('..')

# create async engine for interaction with database
test_engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)

# create async session for interaction with database
test_async_session = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

CLEAN_TABLES = [
    'menus', 'submenus', 'dishes'
]


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def run_migrations():
    pass


@pytest.fixture(scope='session')
async def async_session_test():
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope='function')
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(text(f"""TRUNCATE TABLE {table_for_cleaning} CASCADE;"""))


@pytest.fixture(scope='function')
async def clean_cache(redis_client: aioredis.Redis):
    await redis_client.flushdb()


async def _get_test_db():
    try:
        yield test_async_session()
    finally:
        pass


async def get_redis():
    try:
        logging.warning('Getting redis session...')
        redis = aioredis.ConnectionPool.from_url(
            'redis://redis:6379', decode_responses=True
        )
        logging.warning('Redis connection pool opened successfully :)')
        return redis
    finally:
        logging.warning('Redis connection closed!')


@pytest.fixture(scope='session')
async def redis_client() -> AsyncGenerator:
    async with aioredis.Redis(connection_pool=await get_redis()) as redis:
        yield redis


@pytest.fixture(scope='function')
async def client() -> AsyncGenerator[AsyncClient, Any]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url='http://localhost:8000') as client:
        yield client


@pytest.fixture(scope='session')
async def asyncpg_pool():
    pool = await asyncpg.create_pool(''.join(settings.TEST_DATABASE_URL.split('+asyncpg')))
    yield pool
    pool.close()


# Utility function to create or get existing menu to work with submenu
@pytest.fixture
async def get_menu(client: AsyncClient):
    response = await client.get('/api/v1/menus')
    if not response.json():
        new_menu = await client.post('/api/v1/menus', json={'title': 'New Menu',
                                                            'description': 'New Menu Description'})
        yield str(new_menu.json()['id'])
    else:
        yield str(response.json()[0]['id'])


# Utility function to create or get existing submenu to work with dishes
@pytest.fixture
async def get_submenu(client: AsyncClient, get_menu):
    response = await client.get(f'/api/v1/menus/{get_menu}/submenus')
    if response.json() == []:
        new_submenu = await client.post(f'/api/v1/menus/{get_menu}/submenus', json={'title': 'New Submenu',
                                                                                    'description': 'New Submenu'})
        yield str(new_submenu.json()['id'])
    else:
        yield str(response.json()[0]['id'])
