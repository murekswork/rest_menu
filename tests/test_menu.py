import json
import pytest
from httpx import AsyncClient


class TestMenu:


    @pytest.mark.asyncio
    async def test_read_empty_menus(self, client: AsyncClient, clean_tables):
        response = await client.get("/api/v1/menus")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_menu(self, client: AsyncClient):
        response = await client.post("/api/v1/menus", json={"title": "test menu1",
                                                                'description': "test menu description"})
        assert response.status_code == 201
        assert response.json()['title'] == 'test menu1'
        assert response.json()['description'] == 'test menu description'
        assert response.json()['id'] is not None
        self.created_menu_id = str(response.json()['id'])
        print(self.created_menu_id, 'ITS CREATED MENU ID')
        assert response.json()['dishes_count'] == 0
        assert response.json()['submenus_count'] == 0
        assert response.json()['submenus'] is None
        response = await client.get('/api/v1/menus')

    @pytest.mark.asyncio
    async def test_read_not_empy_menus(self, client: AsyncClient):
        response = await client.get("/api/v1/menus")
        assert response.json() != []
        assert response.status_code == 200


    @pytest.mark.asyncio
    async def test_read_menu(self, client: AsyncClient):
        response = await client.post("/api/v1/menus", json={"title": "test title",
                                                                "description": "test description"})
        menu_id = str(response.json()['id'])
        response = await client.get(f'/api/v1/menus/{menu_id}')
        assert response.status_code == 200
        assert response.json()['title'] == 'test title'
        assert response.json()['description'] == 'test description'

    @pytest.mark.asyncio
    async def test_delete_menu(self, client: AsyncClient, clean_tables):
        response = await client.post('/api/v1/menus', json={"title": "test",
                                                                'description': "test description"})
        menu_id = str(response.json()['id'])
        response = await client.delete(f'/api/v1/menus/{menu_id}')
        assert response.status_code == 200
        assert response.json()['menu_id'] == menu_id
        response = await client.get(f'/api/v1/menus/{menu_id}')
        assert response.json() == {'detail': 'menu not found'}
        response = await client.get('/api/v1/menus')
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_update_menu(self, client: AsyncClient, clean_tables):
        response = await client.post('/api/v1/menus', json={"title": "old title",
                                                                "description": "old description"})
        old_menu = response.json()
        new_response = await client.patch(f'/api/v1/menus/{old_menu["id"]}', json={"title": "new title",
                                                                        "description": "new description"})

        assert old_menu != new_response.json()
        assert new_response.json()['id'] == old_menu['id']
        assert new_response.json()['title'] == 'new title'
        assert new_response.json()['description'] == 'new description'


