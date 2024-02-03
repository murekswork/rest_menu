import json

import aioredis
import pytest
from httpx import AsyncClient

from tests.test_cache.test_cache_service import TestCacheService
from tests.utils import reverse


class TestMenuCacheService(TestCacheService):
    pass


class TestMenuCacheServiceCreate(TestMenuCacheService):

    @pytest.mark.asyncio
    async def test_when_create_menu_correct_cache_appears(self,
                                                          client: AsyncClient,
                                                          redis_client: aioredis.Redis,
                                                          clean_tables):
        response = await client.post(await reverse('menu-create'),
                                     json={'title': 'title', 'description': 'description'})
        assert response.status_code == 201
        cached_menu = json.loads(await redis_client.get(str(response.json()['id'])))
        response_menu = response.json()
        assert cached_menu.keys() == response_menu.keys()
        assert cached_menu['title'] == response_menu['title']
        assert cached_menu['description'] == response_menu['description']
        assert cached_menu['id'] == response_menu['id']

    @pytest.mark.asyncio
    async def test_when_create_menu_menus_list_cache_updates(self,
                                                             client: AsyncClient,
                                                             redis_client: aioredis.Redis,
                                                             clean_tables):
        await client.get(await reverse('menus-read'))
        old_menus_list_cache = (await redis_client.get('menus'))
        await client.post(await reverse('menu-create'),
                          json={'title': 'title', 'description': 'description'})
        new_menus_list_cache = (await redis_client.get('menus'))
        assert new_menus_list_cache != old_menus_list_cache


class TestMenuCacheServiceDelete(TestMenuCacheService):

    @pytest.mark.asyncio
    async def test_when_delete_menu_then_menu_cache_deletes(self,
                                                            client: AsyncClient,
                                                            redis_client: aioredis.Redis,
                                                            clean_tables):
        response = (await client.post(await reverse('menu-create'),
                                      json={'title': 'title', 'description': 'description'})).json()

        old_cache = (await redis_client.get(str(response['id'])))
        await client.delete(await reverse('menu-delete', target_menu_id=response['id']))
        new_cache = (await redis_client.get(str(response['id'])))
        assert old_cache != new_cache
        assert new_cache is None

    @pytest.mark.asyncio
    async def test_when_delete_menu_then_submenu_cache_deletes(self,
                                                               client: AsyncClient,
                                                               redis_client: aioredis.Redis,
                                                               clean_tables):
        menu = await client.post(await reverse('menu-create'),
                                 json={'title': 'title', 'description': 'description'})

        submenu = await client.post(await reverse('submenu-create', target_menu_id=menu.json()['id']),
                                    json={'title': 'title', 'description': 'description'})
        submenu_cache = await redis_client.get(str(submenu.json()['id']))
        assert submenu_cache is not None
        await client.delete(await reverse('menu-delete', target_menu_id=menu.json()['id']))
        new_submenu_cache = await redis_client.get(str(submenu.json()['id']))
        assert new_submenu_cache is None
        assert new_submenu_cache != submenu_cache

    @pytest.mark.asyncio
    async def test_when_delete_menu_then_dish_cache_deletes(self,
                                                            client: AsyncClient,
                                                            redis_client: aioredis.Redis,
                                                            clean_tables):
        menu = await client.post(await reverse('menu-create'), json={'title': 'title', 'description': 'description'})
        assert menu.status_code == 201
        submenu = await client.post(await reverse('submenu-create', target_menu_id=menu.json()['id']),
                                    json={'title': 'title', 'description': 'description'})
        assert submenu.status_code == 201
        dish = await client.post(await reverse('dish-create',
                                               target_menu_id=menu.json()['id'],
                                               target_submenu_id=submenu.json()['id']),
                                 json={'title': 'title',
                                       'description': 'description',
                                       'price': 99})
        assert dish.status_code == 201
        dish_cache = await redis_client.get(str(dish.json()['id']))
        assert dish_cache is not None
        await client.delete(await reverse('menu-delete', target_menu_id=menu.json()['id']))
        new_dish_cache = await redis_client.get(str(dish.json()['id']))
        assert new_dish_cache is None
        assert dish_cache != new_dish_cache

    @pytest.mark.asyncio
    async def test_when_delete_menu_then_submenus_list_cache_deletes(self,
                                                                     client: AsyncClient,
                                                                     redis_client: aioredis.Redis,
                                                                     clean_tables):
        menu = await client.post(await reverse('menu-create'), json={'title': 'title',
                                                                     'description': 'description'})
        assert menu.status_code == 201
        submenu = await client.post(await reverse('submenu-create', target_menu_id=menu.json()['id']),
                                    json={'title': 'title', 'description': 'description'})
        await client.post(await reverse('submenu-create', target_submenu_id=submenu.json()['id']),
                          json={'title': 'title', 'description': 'description'})
        response = await client.get(await reverse('submenu-read-list', target_menu_id=menu.json()['id']))
        assert response.status_code == 200
        submenu_list_cache = await redis_client.get(f'{menu.json()["id"]}_submenus')
        assert submenu_list_cache is not None
        delete = await client.delete(await reverse('menu-delete', target_menu_id=menu.json()['id']))
        assert delete.status_code == 200
        new_submenu_list_cache = await redis_client.get(f'{menu.json()["id"]}_submenus')
        assert new_submenu_list_cache != submenu_list_cache
        assert new_submenu_list_cache is None

    @pytest.mark.asyncio
    async def test_when_delete_menu_then_submenu_dish_list_deleted(self,
                                                                   client: AsyncClient,
                                                                   redis_client: aioredis.Redis,
                                                                   clean_tables):
        menu = await client.post(await reverse('menu-create'), json={'title': 'title', 'description': 'description'})
        assert menu.status_code == 201
        submenu = await client.post(await reverse('submenu-create', target_menu_id=menu.json()['id']),
                                    json={'title': 'title', 'description': 'description'})
        assert submenu.status_code == 201
        dish = await client.post(await reverse('dish-create',
                                               target_menu_id=menu.json()['id'],
                                               target_submenu_id=submenu.json()['id']),
                                 json={'title': 'title',
                                       'description': 'description',
                                       'price': 99})
        assert dish.status_code == 201
        list_dishes_response = await client.get(await reverse('dish-list',
                                                              target_menu_id=menu.json()['id'],
                                                              target_submenu_id=submenu.json()['id']))
        assert list_dishes_response.status_code == 200
        list_dishes_cache = await redis_client.get(f"{submenu.json()['id']}_dishes")
        assert list_dishes_cache is not None
        menu_delete = await client.delete(await reverse('menu-delete', target_menu_id=menu.json()['id']))
        assert menu_delete.status_code == 200
        new_dishes_cache = await redis_client.get(f"{submenu.json()['id']}_dishes")
        assert new_dishes_cache != list_dishes_cache
        assert new_dishes_cache is None


class TestMenuCacheServiceUpdate(TestMenuCacheService):

    @pytest.mark.asyncio
    async def test_when_update_menu_then_menu_cache_updates_correct(self,
                                                                    client: AsyncClient,
                                                                    redis_client: aioredis.Redis,
                                                                    clean_tables):
        menu = await client.post(await reverse('menu-create'), json={'title': 'title', 'description': 'description'})
        assert menu.status_code == 201
        menu_cache = await redis_client.get(f"{menu.json()['id']}")
        assert menu_cache is not None
        update_menu = await client.patch(await reverse('menu-patch', target_menu_id=menu.json()['id']),
                                         json={'title': 'new-title', 'description': 'new-description'})
        assert update_menu.status_code == 200
        menu_new_cache = await redis_client.get(f"{menu.json()['id']}")
        assert menu_new_cache is not None
        assert menu_new_cache != menu_cache
        menu_new_cache = json.loads(menu_new_cache)
        update_menu_json = update_menu.json()
        assert menu_new_cache.keys() == update_menu_json.keys()
        assert menu_new_cache['title'] == update_menu_json['title']
        assert menu_new_cache['description'] == update_menu_json['description']
        assert menu_new_cache['id'] == update_menu_json['id']

    @pytest.mark.asyncio
    async def test_when_update_menu_then_menu_counts_cache_deletes(self,
                                                                   client: AsyncClient,
                                                                   redis_client: aioredis.Redis,
                                                                   clean_tables):
        menu = await client.post(await reverse('menu-create'), json={'title': 'title', 'description': 'description'})
        assert menu.status_code == 201
        menu_counts = await client.get(await reverse('menu-read-counts', target_menu_id=menu.json()['id']))
        assert menu_counts.status_code == 200
        menu_counts_cache = await redis_client.get(f"{menu.json()['id']}_counts")
        assert menu_counts_cache is not None
        update_menu = await client.patch(await reverse('menu-patch', target_menu_id=menu.json()['id']),
                                         json={'title': 'new-title', 'description': 'new-description'})
        assert update_menu.status_code == 200
        menu_new_counts_cache = await redis_client.get(f"{menu.json()['id']}_counts")
        assert menu_new_counts_cache is None
        assert menu_new_counts_cache != menu_counts_cache
