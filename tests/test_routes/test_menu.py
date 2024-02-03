import pytest
from httpx import AsyncClient

from tests.utils import reverse


class TestMenu:

    # Test that by default app does not have unexpected menus
    @pytest.mark.asyncio
    async def test_read_empty_menus(self, client: AsyncClient, clean_tables):
        response = await client.get(await reverse('menus-read'))
        assert response.status_code == 200
        assert response.json() == []

    # Test that create app route works properly and created menu can have right fields
    @pytest.mark.asyncio
    async def test_create_menu(self, client: AsyncClient):
        response = await client.post(await reverse('menu-create'), json={'title': 'test menu1',
                                                                         'description': 'test menu description'})
        assert response.status_code == 201
        assert response.json()['title'] == 'test menu1'
        assert response.json()['description'] == 'test menu description'
        assert response.json()['id'] is not None
        assert response.json()['dishes_count'] == 0
        assert response.json()['submenus_count'] == 0
        assert response.json()['submenus'] == []
        response = await client.get('/api/v1/menus')

    # Test that after menu creation menus read route show created menu
    @pytest.mark.asyncio
    async def test_read_not_empy_menus(self, client: AsyncClient):
        response = await client.get(await reverse('menus-read'))
        assert response.json() != []
        assert response.status_code == 200

    # Test that created menu can be read
    @pytest.mark.asyncio
    async def test_read_menu(self, client: AsyncClient):
        response = await client.post(await reverse('menu-create'), json={'title': 'test title',
                                                                         'description': 'test description'})
        menu_id = str(response.json()['id'])
        response = await client.get(await reverse('menu-read', target_menu_id=menu_id))
        assert response.status_code == 200
        assert response.json()['title'] == 'test title'
        assert response.json()['description'] == 'test description'

    # Test that menu deletes route work properly
    @pytest.mark.asyncio
    async def test_delete_menu(self, client: AsyncClient, clean_tables):
        response = await client.post(await reverse('menu-create'), json={'title': 'test',
                                                                         'description': 'test description'})
        menu_id = str(response.json()['id'])
        response = await client.delete(await reverse('menu-delete', target_menu_id=menu_id))
        assert response.status_code == 200
        assert response.json()['menu_id'] == menu_id
        response = await client.get(await reverse('menu-read', target_menu_id=menu_id))
        assert response.json() == {'detail': 'menu not found'}
        response = await client.get(await reverse('menus-read'))
        assert response.json() == []

    # Test that menu update route work properly and changes are saving
    @pytest.mark.asyncio
    async def test_update_menu(self, client: AsyncClient, clean_tables):
        response = await client.post(await reverse('menu-create'),
                                     json={'title': 'old title',
                                           'description': 'old description'})
        old_menu = response.json()
        new_response = await client.patch(await reverse('menu-patch', target_menu_id=old_menu['id']),
                                          json={'title': 'new title',
                                                'description': 'new description'})

        assert old_menu != new_response.json()
        assert new_response.json()['id'] == old_menu['id']
        assert new_response.json()['title'] == 'new title'
        assert new_response.json()['description'] == 'new description'
