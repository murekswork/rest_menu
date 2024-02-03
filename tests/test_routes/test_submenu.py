import pytest
from httpx import AsyncClient


class TestSubmenu:

    # Test if created menu have not submenus
    @pytest.mark.asyncio
    async def test_read_menu_submenus_when_empty(self, client: AsyncClient, clean_tables, get_menu):
        response = await client.get(f'/api/v1/menus/{get_menu}/submenus')
        assert response.status_code == 200
        assert response.json() == []

    # Create submenu then read it
    @pytest.mark.asyncio
    async def test_create_submenu(self, client: AsyncClient, get_menu):
        response = await client.post(f'/api/v1/menus/{get_menu}/submenus', json={'title': 'test',
                                                                                 'description': 'test desc'})
        assert response.status_code == 201
        assert response.json()['title'] == 'test'
        assert response.json()['description'] == 'test desc'

    # Test if created submenu appears in menu submenus
    @pytest.mark.asyncio
    async def test_read_menu_submenus_when_not_empty(self, client: AsyncClient, get_menu):
        response = await client.get(f'/api/v1/menus/{get_menu}/submenus')
        assert response.status_code == 200
        assert response.json() != []

    # Firstly create new submenu, then read this submenu
    @pytest.mark.asyncio
    async def test_read_submenu(self, client: AsyncClient, clean_tables, get_menu):
        submenu = await client.post(f'/api/v1/menus/{get_menu}/submenus',
                                    json={'title': 'title',
                                          'description': 'description'})
        submenu_id = str(submenu.json()['id'])

        response = await client.get(f'/api/v1/menus/{get_menu}/submenus/{submenu_id}')
        assert response.status_code == 200
        assert response.json()['title'] == 'title'
        assert response.json()['description'] == 'description'

    # Test update submenu. First create new submenu read its title, description and save id, then update and
    # read same submenu with same id but get updated title and description
    @pytest.mark.asyncio
    async def test_update_submenu(self, client: AsyncClient, clean_tables, get_menu):
        submenu = await client.post(f'/api/v1/menus/{get_menu}/submenus',
                                    json={'title': 'title',
                                          'description': 'description'})

        submenu_id = str(submenu.json()['id'])

        response = await client.patch(f'/api/v1/menus/{get_menu}/submenus/{submenu_id}',
                                      json={'title': 'new title',
                                            'description': 'new description'})
        assert response.status_code == 200
        patched_submenu = await client.get(f'/api/v1/menus/{get_menu}/submenus/{submenu_id}')
        assert patched_submenu.json()['title'] == 'new title'
        assert patched_submenu.json()['description'] == 'new description'
        assert patched_submenu.json()['id'] == submenu_id

    # Test delete submenu. Firstly create new submenu, read that it exist, then delete, read and get
    # submenu not found, also check that submenu deleted from menu.submenus
    @pytest.mark.asyncio
    async def test_delete_submenu(self, client: AsyncClient, clean_tables, get_menu):
        submenu = await client.post(f'/api/v1/menus/{get_menu}/submenus',
                                    json={'title': 'title',
                                          'description': 'description'})
        submenu_id = str(submenu.json()['id'])
        submenu_read = await client.get(f'/api/v1/menus/{get_menu}/submenus/{submenu_id}')
        assert submenu_read.json()['title'] == 'title'
        assert submenu_read.json()['description'] == 'description'
        menu_submenus = await client.get(f'/api/v1/menus/{get_menu}/submenus')
        assert menu_submenus.json() != list(submenu_read.json(), )
        response = await client.delete(f'/api/v1/menus/{get_menu}/submenus/{submenu_id}')
        check_submenu = await client.get(f'/api/v1/menus/{get_menu}/submenus/{submenu_id}')
        assert check_submenu.json() == {'detail': 'submenu not found'}
        menu_submenus = await client.get(f'/api/v1/menus/{get_menu}/submenus')
        assert response.status_code == 200
        assert menu_submenus.json() == []
