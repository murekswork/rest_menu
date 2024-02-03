import sys

import pytest
from httpx import AsyncClient

from tests.utils import reverse

sys.path.append('..')


class TestReverse:

    @pytest.mark.asyncio
    async def test_reverse_returns_correct_url(self, client: AsyncClient):
        reverse_url = await reverse('menu-create')
        assert reverse_url == '/api/v1/menus'

    # async def asdasd(self):
    #     response = await client.get(await reverse('menus'))
    #     assert response.url ==
    #     assert response.status_code == 200
