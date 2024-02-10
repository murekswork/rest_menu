import json

import aioredis
import pytest
from httpx import AsyncClient

from tests.test_cache.test_cache_service import TestCacheService
from tests.utils import reverse


class TestSubmenuCacheService(TestCacheService):
    pass


class TestSubmenuCacheServiceCreate(TestSubmenuCacheService):

    @pytest.mark.asyncio
    async def test_when_create_submenu_correct_cache_appears(
            self,
            client: AsyncClient,
            redis_client: aioredis.Redis,
            clean_tables):
        menu = await client.post(await reverse('menu-create'),
                                 json={'title': 'title',
                                       'description': 'description'})
        assert menu.status_code == 201
        submenu = await client.post(
            await reverse('submenu-create', target_menu_id=menu.json()['id']),
            json={'title': 'title', 'description': 'description'})
        assert submenu.status_code == 201
        submenu_cache = json.loads(
            await redis_client.get(submenu.json()['id']))
        assert submenu_cache.keys() == submenu.json().keys()
        assert submenu_cache['title'] == 'title'
        assert submenu_cache['description'] == 'description'
        assert submenu_cache['id'] == submenu.json()['id']

    @pytest.mark.asyncio
    async def test_when_create_submenu_then_menu_cache_deletes(
            self,
            client: AsyncClient,
            redis_client: aioredis.Redis,
            clean_tables):
        menu = await client.post(await reverse('menu-create'),
                                 json={'title': 'title',
                                       'description': 'description'})
        assert menu.status_code == 201

        response_menu_submenus = await client.get(
            await reverse('submenu-read-list',
                          target_menu_id=menu.json()['id']))
        assert response_menu_submenus.status_code == 200

        response_menu_counts = await client.get(
            await (reverse('menu-read-counts',
                           target_menu_id=menu.json()['id'])))
        assert response_menu_counts.status_code == 200

        menu_cache = json.loads(await redis_client.get(menu.json()['id']))
        menu_submenus_cache = json.loads(
            await redis_client.get(f"{menu.json()['id']}_submenus"))
        menu_counts_cache = json.loads(
            await redis_client.get(f"{menu.json()['id']}_counts"))

        assert menu_cache is not None
        assert menu_submenus_cache is not None
        assert menu_counts_cache is not None

        assert menu_cache
        submenu = await client.post(await reverse('submenu-create',
                                                  target_menu_id=menu.json()[
                                                      'id']),
                                    json={'title': 'title',
                                          'description': 'description'})
        assert submenu.status_code == 201

        menu_cache_new = await redis_client.get(menu.json()['id'])
        menu_submenus_cache_new = await redis_client.get(
            f"{menu.json()['id']}_submenus")
        menu_counts_cache_new = await redis_client.get(
            f"{menu.json()['id']}_counts")

        assert menu_cache_new is None
        assert menu_submenus_cache_new is None
        assert menu_counts_cache_new is None


class TestSubmenuCacheServiceDelete:

    @pytest.mark.asyncio
    async def test_when_delete_submenu_then_menu_cache_deletes(
            self,
            client: AsyncClient,
            redis_client: aioredis.Redis,
            clean_tables):
        menu = await client.post(await reverse('menu-create'),
                                 json={'title': 'title',
                                       'description': 'description'})
        assert menu.status_code == 201
        submenu = await client.post(await reverse('submenu-create',
                                                  target_menu_id=menu.json()[
                                                      'id']),
                                    json={'title': 'title',
                                          'description': 'description'})
        assert submenu.status_code == 201
        await client.get(
            await reverse('menu-read', target_menu_id=menu.json()['id']))
        assert await redis_client.get(f"{menu.json()['id']}") is not None
        delete = await client.delete(await reverse('submenu-delete',
                                                   target_menu_id=menu.json()[
                                                       'id'],
                                                   target_submenu_id=submenu.json()['id']))
        assert delete.status_code == 200
        assert await redis_client.get(f'{menu.json()}') is None

    @pytest.mark.asyncio
    async def test_when_delete_submenu_then_menu_submenus_cache_deletes(
            self,
            client: AsyncClient,
            redis_client: aioredis.Redis,
            clean_tables):
        menu = await client.post(await reverse('menu-create'),
                                 json={'title': 'title',
                                       'description': 'description'})
        assert menu.status_code == 201
        submenu = await client.post(await reverse('submenu-create',
                                                  target_menu_id=menu.json()[
                                                      'id']),
                                    json={'title': 'title',
                                          'description': 'description'})
        assert submenu.status_code == 201
        menu_submenus = await client.get(await reverse('submenu-read-list',
                                                       target_menu_id=menu.json()['id']))
        assert menu_submenus.status_code == 200
        assert await redis_client.get(
            f"{menu.json()['id']}_submenus") is not None
        delete = await client.delete(await reverse('submenu-delete',
                                                   target_menu_id=menu.json()[
                                                       'id'],
                                                   target_submenu_id=submenu.json()['id']))
        assert delete.status_code == 200
        assert await redis_client.get(f'{menu.json()["id"]}_submenus') is None

    @pytest.mark.asyncio
    async def test_when_delete_submenu_then_menus_cache_deletes(
            self,
            client: AsyncClient,
            redis_client: aioredis.Redis,
            clean_tables):
        menu = await client.post(await reverse('menu-create'),
                                 json={'title': 'title',
                                       'description': 'description'})
        assert menu.status_code == 201
        submenu = await client.post(await reverse('submenu-create',
                                                  target_menu_id=menu.json()[
                                                      'id']),
                                    json={'title': 'title',
                                          'description': 'description'})
        assert submenu.status_code == 201
        await client.get(await reverse('menus-read'))
        assert await redis_client.get('menus') is not None
        delete = await client.delete(await reverse('submenu-delete',
                                                   target_menu_id=menu.json()[
                                                       'id'],
                                                   target_submenu_id=submenu.json()['id']))
        assert delete.status_code == 200
        assert await redis_client.get('menus') is None

    @pytest.mark.asyncio
    async def test_when_delete_submenu_then_menu_counts_cache_deletes(
            self,
            client: AsyncClient,
            redis_client: aioredis.Redis,
            clean_tables):
        menu = await client.post(await reverse('menu-create'),
                                 json={'title': 'title',
                                       'description': 'description'})
        assert menu.status_code == 201
        submenu = await client.post(await reverse('submenu-create',
                                                  target_menu_id=menu.json()[
                                                      'id']),
                                    json={'title': 'title',
                                          'description': 'description'})
        assert submenu.status_code == 201
        menu_counts = await client.get(await reverse('menu-read-counts',
                                                     target_menu_id=menu.json()['id']))
        assert menu_counts.status_code == 200
        assert await redis_client.get(
            f"{menu.json()['id']}_counts") is not None
        delete = await client.delete(await reverse('submenu-delete',
                                                   target_submenu_id=submenu.json()['id'],
                                                   target_menu_id=menu.json()[
                                                       'id']))
        assert delete.status_code == 200
        assert await redis_client.get(f"{menu.json()['id']}_counts") is None
