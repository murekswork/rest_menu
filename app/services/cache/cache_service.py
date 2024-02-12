import json
from uuid import UUID

import aioredis
from fastapi import Depends
from pydantic import BaseModel

from app.db.session import get_redis
from app.schemas.menu_schemas import MenuRead, MenuReadCounts
from app.schemas.submenu_schemas import SubmenuRead


class CacheService:

    def __init__(self, cache: aioredis.Redis = Depends(get_redis)) -> None:
        self.cache = cache

    @staticmethod
    async def deserialize_schema(schema: type[BaseModel]) -> str:
        schema.id = str(schema.id)
        return schema.model_dump_json()

    @staticmethod
    async def serialize_schema(json_str: str,
                               schema: type[BaseModel]) -> BaseModel:
        return schema(**json.loads(json_str))

    async def set_list(self, key: UUID | str, value: list[BaseModel]) -> None:
        serialized_list = [val.model_dump_json() for val in value]
        await self.cache.set(str(key), json.dumps(serialized_list))

    async def get_model_cache(self,
                              key: str | UUID,
                              schema: type[BaseModel]) -> BaseModel | None:
        """Function checks for cache wth received key and return schema or None"""
        value = await self.cache.get(str(key))
        if value is None:
            return None
        result = await self.serialize_schema(value, schema)
        return result

    async def get_model_list_cache(self,
                                   key: str | None,
                                   schema: type[BaseModel]
                                   ) -> list[BaseModel] | None:
        """
        Function used to get many cached schemas it checks for cache with received key
        and returns list of schemas value or None
        """
        cached_list = await self.cache.get(key)
        if cached_list is None:
            return None
        return [schema(**json.loads(cache)) for cache in
                json.loads(cached_list)]

    async def set_model_cache(self, key: UUID, value: type[BaseModel]) -> None:
        await self.cache.set(str(key), await self.deserialize_schema(value))

    async def check_sale(self, dish_id: UUID) -> None | str:
        sales_data = await self.cache.get('sales_data')

        if sales_data is None:
            return None

        sales = json.loads(sales_data.replace("'", '"'))
        if str(dish_id) not in sales:
            return None
        return sales[str(dish_id)]


class MenuCacheService(CacheService):

    async def invalidate_menu_cache(self, menu: MenuRead) -> None:
        """
        Function used to invalidate menu cache with all related values.
        Function takes menu schema, create list of ids,
        then fills it  with all related submenus and dishes id by using loop
        and deletes from cache each value from list
        """
        ids = [menu.id, 'menus', f'{menu.id}_counts', f'{menu.id}_submenus']
        if menu.submenus is not None:
            for submenu in menu.submenus:
                if submenu.dishes:
                    for dish in submenu.dishes:
                        ids.append(dish.id)
                ids.append(submenu.id)
                ids.append(f'{submenu.id}_dishes')
        for item in ids:
            await self.cache.delete(str(item))

    async def create_menu_cache(self, key: UUID | str,
                                value: MenuRead) -> None:
        await self.cache.delete('menus')
        deserialized_schema = await self.deserialize_schema(value)
        await self.cache.set(str(key), deserialized_schema)

    async def update_menu_cache(self, key: UUID, value: MenuRead) -> None:
        await self.cache.delete('menus')
        await self.cache.delete(f'{key}_counts')
        value.id = str(value.id)
        await self.cache.set(str(key), json.dumps(value.model_dump()))

    async def set_menu_cache_with_counts(self, key: UUID,
                                         value: MenuReadCounts) -> None:
        await self.cache.set(f'{key}_counts',
                             await self.deserialize_schema(value))


class SubmenuCacheService(CacheService):

    async def invalidate_submenu_cache(self, submenu: SubmenuRead,
                                       menu_id) -> None:
        """
        Function used to invalidate submenu cache with all related values.
        Function takes submenu schema and menu id, creates list of ids,
        then fills it by using loop and deletes from cache each value from list
        """
        ids = [menu_id, f'{menu_id}_submenus', f'{menu_id}_counts', 'menus']
        if submenu.dishes:
            for dish in submenu.dishes:
                ids.append(dish.id)
        ids.append(submenu.id)
        for id in ids:
            await self.cache.delete(str(id))

    async def update_submenu_cache(self, menu_id: UUID,
                                   submenu: SubmenuRead) -> None:
        [await self.cache.delete(str(key)) for key in ['menus',
                                                       f'{menu_id}',
                                                       f'{menu_id}_submenus',
                                                       f'{menu_id}_counts',
                                                       ]]
        await self.cache.set(str(submenu.id),
                             await self.deserialize_schema(submenu))


class DishCacheService(CacheService):

    async def invalidate_dish_cache(self, key: UUID, submenu_key: UUID,
                                    menu_key: UUID) -> None:
        [await self.cache.delete(str(key)) for key in [key,
                                                       menu_key,
                                                       submenu_key,
                                                       'menus'
                                                       f'{menu_key}_counts',
                                                       f'{menu_key}_submenus',
                                                       f'{submenu_key}_dishes',
                                                       ]]
