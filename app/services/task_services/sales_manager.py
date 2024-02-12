import json
from uuid import UUID

import aioredis

from app.db.models import Dish
from app.db.repository.utils import AdvancedMenuRepository


class SalesManager:

    def __init__(self,
                 redis: aioredis.Redis,
                 database_manager: AdvancedMenuRepository) -> None:
        self.redis = redis
        self.database_manager = database_manager

    async def delete_old_sales(self) -> None:
        """Method deletes old sales data"""
        old_sales = await self.get_old_sales_data()
        if old_sales is not None:
            for sale in old_sales:
                await self.redis.delete(sale)
        await self.redis.delete('sales_data', 'menus')

    async def fill_new_sales(self, sale_dishes: list[dict]) -> None:
        """Method creates new sales data"""
        new_sales_data = await self.create_new_sales(sale_dishes)
        await self.redis.set('sales_data', str(new_sales_data))

    async def get_old_sales_data(self) -> dict | None:
        """Method gets old sales data"""
        old_sales = await self.redis.get('sales_data')
        if old_sales is not None:
            return json.loads(old_sales.replace("'", '"'))
        return None

    async def create_new_sales(self, sale_dishes: list[dict]) -> dict:
        """
        Method create sales_data dict and fills it with dish id: sale value
        then sets 'sales_data' key in cache
        """
        new_sales_data = {}
        for dish in sale_dishes:
            dish_id = await self.get_dish_id(dish['title'],
                                             dish['description'])
            new_sales_data[str(dish_id)] = dish['sale']
        await self.redis.set('sales_data', str(new_sales_data))
        return new_sales_data

    async def get_dish_id(self, title: str, description: str) -> str | UUID:
        """Method to get dish id by title and description with db manager"""
        dish_id = await self.database_manager.read_by_title_description(
            obj_class=Dish,
            title=title,
            description=description)
        return dish_id
