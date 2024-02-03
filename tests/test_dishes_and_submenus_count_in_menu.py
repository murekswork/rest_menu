import pytest
from httpx import AsyncClient


class TestDishesAndSubmenusCountInMenu:

    # At the beginning of the test fixtures clean all database tables data,
    # according test requirements creates menu and its submenu, then test creates first dish
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

    # Test creates second dish for submenu from previous test
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

    # Test that menu counts route works properly and return 1 submenu and 2 dishes in created menu
    @pytest.mark.asyncio
    async def test_menu_has_counts(self, client: AsyncClient, get_menu):
        response = await client.get(f'/api/v1/menus/{get_menu}/counts')
        assert response.status_code == 200
        assert response.json()['submenus_count'] == 1
        assert response.json()['dishes_count'] == 2

    # Test that submenu route return right dishes count
    @pytest.mark.asyncio
    async def test_submenu_has_count(self, client: AsyncClient, get_menu, get_submenu):
        response = await client.get(f'/api/v1/menus/{get_menu}/submenus/{get_submenu}')
        assert response.status_code == 200
        assert response.json()['dishes_count'] == 2

    # Deletes submenu
    @pytest.mark.asyncio
    async def test_delete_submenu(self, client: AsyncClient, get_menu, get_submenu):
        response = await client.delete(f'/api/v1/menus/{get_menu}/submenus/{get_submenu}')
        assert response.status_code == 200

    # Test that submenus route returns empty list.
    @pytest.mark.asyncio
    async def test_menu_submenus_list(self, client: AsyncClient, get_menu):
        response = await client.get(f'/api/v1/menus/{get_menu}/submenus')
        assert response.status_code == 200
        assert response.json() == []

    # Test that menu route return 0 dishes and submenus counts after submenu deletion

    @pytest.mark.asyncio
    async def test_menu_after_submenu_delete(self, client: AsyncClient, get_menu):
        response = await client.get(f'/api/v1/menus/{get_menu}/counts')
        assert response.status_code == 200
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0

    # Deletes menu
    @pytest.mark.asyncio
    async def test_delete_menu(self, client: AsyncClient, get_menu):
        response = await client.delete(f'/api/v1/menus/{get_menu}')
        assert response.status_code == 200

    # Test that menus route return empty list after deletion
    @pytest.mark.asyncio
    async def test_menus_list(self, client: AsyncClient):
        response = await client.get('/api/v1/menus')
        assert response.status_code == 200
        assert response.json() == []
