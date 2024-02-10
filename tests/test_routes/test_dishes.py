import pytest
from httpx import AsyncClient


class TestDishes:

    # Test that created submenu does not have dishes
    @pytest.mark.asyncio
    async def test_read_submenu_with_empty_dishes(
            self,
            client: AsyncClient,
            clean_tables,
            get_menu,
            get_submenu) -> None:
        response = await client.get(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes')
        assert response.status_code == 200
        assert response.json() == []

    # Test that create dish work and check created dish fields
    @pytest.mark.asyncio
    async def test_create_dish(
            self,
            client: AsyncClient,
            get_menu,
            get_submenu):
        response = await client.post(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes',
            json={'title': 'New dish',
                  'description': 'New dish description',
                  'price': 123})
        assert response.status_code == 201
        assert response.json()['title'] == 'New dish'
        assert response.json()['description'] == 'New dish description'
        assert response.json()['price'] == '123.00'

    # Test that created dish appears in submenu.dishes
    @pytest.mark.asyncio
    async def test_read_submenu_with_dishes(
            self,
            client: AsyncClient,
            get_menu, get_submenu):
        response = await client.get(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes')
        assert response.status_code == 200
        assert response.json() != []

    # Test read created dish can be read. Create dish then try to read it
    @pytest.mark.asyncio
    async def test_read_submenu_without_dishes(self,
                                               clean_tables,
                                               clean_cache,
                                               client: AsyncClient,
                                               get_menu,
                                               get_submenu):
        dish = await client.post(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes',
            json={'title': 'title',
                  'description': 'description',
                  'price': 123})
        dish_id = dish.json()['id']
        response = await client.get(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes/{str(dish_id)}')
        assert response.status_code == 200
        assert response.json()['title'] == 'title'
        assert response.json()['description'] == 'description'
        assert response.json()['price'] == '123.00'

    # Test that dish can be updated. Firstly create dish, then read old values,
    # then patch and get new values

    @pytest.mark.asyncio
    async def test_patch_dish(self, client: AsyncClient, clean_tables,
                              clean_cache, get_menu, get_submenu):
        response = await client.post(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes',
            json={'title': 'title',
                  'description': 'description',
                  'price': 123})
        assert response.status_code == 201
        old_dish = response.json()
        old_dish_id = str(old_dish['id'])
        response = await client.get(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes/{old_dish_id}')
        assert response.status_code == 200
        assert response.json()['title'] == 'title'
        assert response.json()['description'] == 'description'
        assert response.json()['price'] == '123.00'
        response = await client.patch(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes/{old_dish_id}',
            json={'title': 'new title',
                  'description': 'new description',
                  'price': 321})
        assert response.status_code == 200
        assert response.json()['title'] == 'new title'
        assert response.json()['description'] == 'new description'
        assert response.json()['price'] == '321.00'
        assert str(response.json()['id']) == old_dish_id

    # Test delete created dish

    @pytest.mark.asyncio
    async def test_put_dish(self, client: AsyncClient, clean_tables,
                            clean_cache, get_menu, get_submenu):
        response = await client.post(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes',
            json={'title': 'new title',
                  'description': 'new description',
                  'price': 123})
        assert response.status_code == 201
        dish_id = str(response.json()['id'])
        response = await client.get(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes/{dish_id}')
        assert response.status_code == 200
        response = await client.delete(
            f'api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes/{dish_id}')
        assert response.status_code == 200
        response = await client.get(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes/{dish_id}')
        assert response.status_code == 404
        response = await client.get(
            f'/api/v1/menus/{get_menu}/submenus/{get_submenu}/dishes')
        assert response.json() == []
