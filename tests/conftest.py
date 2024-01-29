import sys

sys.path.append("..")

from typing import Generator, Any
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from httpx import AsyncClient
import settings
from main import app
import os
import asyncio
from db.session import get_db
import asyncpg

# create async engine for interaction with database
test_engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)

# create async session for interaction with database
test_async_session = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

CLEAN_TABLES = [
    "menus", 'submenus', 'dishes'
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def run_migrations():
    pass


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope="function")
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(text(f"""TRUNCATE TABLE {table_for_cleaning} CASCADE;"""))


async def _get_test_db():
    try:
        yield test_async_session()
    finally:
        pass


@pytest.fixture(scope="function")
async def client() -> Generator[AsyncClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url='http://localhost:8000') as client:
        yield client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool("".join(settings.TEST_DATABASE_URL.split("+asyncpg")))
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
        print(new_submenu.json())
        yield str(new_submenu.json()['id'])
    else:
        yield str(response.json()[0]['id'])
