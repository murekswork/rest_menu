import pytest
import json
from httpx import AsyncClient


class TestDishesAndSubmenusCountInMenu:

    @pytest.mark.asyncio
    async def test_create_first_dish(self, client: AsyncClient, clean_tables, get_menu, get_submenu):
        response = await client.post(f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes',
                                     json={'title': 'Test Dish 1',
                                           'description': 'Test dish description',
                                           'price': 123}
                                     )
        assert response.status_code == 201
        assert response.json()['title'] == 'Test Dish 1'
        assert response.json()['description'] == 'Test dish description'
        assert response.json()['price'] == '123.00'

    @pytest.mark.asyncio
    async def test_create_second_dish(self, client: AsyncClient, get_menu, get_submenu):
        response = await client.post(f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes',
                                     json={'title': 'Test Dish 2',
                                           'description': 'Test dish description',
                                           'price': 321}
                                     )
        assert response.status_code == 201
        assert response.json()['title'] == 'Test Dish 2'
        assert response.json()['description'] == 'Test dish description'
        assert response.json()['price'] == '321.00'

    @pytest.mark.asyncio
    async def test_menu_has_counts(self, client: AsyncClient, get_menu):
        response = await client.get(f'/api/v1/menus/{get_menu}/counts')
        assert response.status_code == 200
        assert response.json()['submenus_count'] == 1
        assert response.json()['dishes_count'] == 2

    @pytest.mark.asyncio
    async def test_submenu_has_count(self, client: AsyncClient, get_menu, get_submenu):
        response = await client.get(f'/api/v1/menus/{get_menu}/submenus/{get_submenu}')
        assert response.status_code == 200
        assert response.json()['dishes_count'] == 2

    @pytest.mark.asyncio
    async def test_delete_submenu(self, client: AsyncClient, get_menu, get_submenu):
        response = await client.delete(f'/api/v1/menus/{get_menu}/submenus/{get_submenu}')
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_menu_submenus_list(self, client: AsyncClient, get_menu):
        response = await client.get(f'/api/v1/menus/{get_menu}/submenus')
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_submenu_dishes_count(self, client: AsyncClient, get_menu, get_submenu):
        response = await client.get(f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes')
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_submenu_dishes_count(self, client: AsyncClient, get_menu):
        response = await client.get(f'/api/v1/menus/{get_menu}/counts')
        assert response.status_code == 200
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0

    @pytest.mark.asyncio
    async def test_delete_menu(self, client: AsyncClient, get_menu):
        response = await client.delete(f'/api/v1/menus/{get_menu}')
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_menus_list(self, client: AsyncClient):
        response = await client.get(f'/api/v1/menus')
        assert response.status_code == 200
        assert response.json() == []