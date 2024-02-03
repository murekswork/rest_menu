import json
from uuid import UUID

import aioredis
from pydantic import BaseModel

from app.schemas.dish_schemas import DishRead
from app.schemas.menu_schemas import MenuRead, MenuReadCounts
from app.schemas.submenu_schemas import SubmenuRead


class CacheService:

    def __init__(self, redis: aioredis.ConnectionPool) -> None:
        self.cache = aioredis.Redis(connection_pool=redis)

    @staticmethod
    async def deserialize_schema(schema: type[BaseModel]) -> str:
        schema.id = str(schema.id)
        return schema.model_dump_json()

    @staticmethod
    async def serialize_schema(json_str: str, schema: type[BaseModel]) -> BaseModel:
        return schema(**json.loads(json_str))

    async def set_list(self, key: UUID | str, value: list[type[BaseModel]]) -> None:
        serialized_list = [val.model_dump_json() for val in value]
        await self.cache.set(str(key), json.dumps(serialized_list))

    async def get_model_cache(self, key: str, schema: type[BaseModel]) -> BaseModel | None:
        value = await self.cache.get(str(key))
        if value is None:
            return None
        result = await self.serialize_schema(value, schema)
        return result

    async def set_model_cache(self, key: UUID, value: type[BaseModel]):
        await self.cache.set(str(key), await self.deserialize_schema(value))


class MenuCacheService(CacheService):

    async def invalidate_menu_cache(self, menu: type[MenuRead]):
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

    async def create_menu_cache(self, key: UUID, value: MenuRead):
        await self.cache.delete('menus')
        deserialized_schema = await self.deserialize_schema(value)
        await self.cache.set(str(key), deserialized_schema)

    async def update_menu_cache(self, key: UUID, value: MenuRead):
        await self.cache.delete('menus')
        await self.cache.delete(f'{key}_counts')
        value.id = str(value.id)
        await self.cache.set(str(key), json.dumps(value.model_dump()))

    async def set_menu_cache_with_counts(self, key: UUID, value: MenuReadCounts):
        await self.cache.set(f'{key}_counts', await self.deserialize_schema(value))


class SubmenuCacheService(CacheService):

    async def invalidate_submenu_cache(self, submenu: SubmenuRead, menu_id):
        ids = [menu_id, f'{menu_id}_submenus', f'{menu_id}_counts']
        if submenu.dishes:
            for dish in submenu.dishes:
                ids.append(dish.id)
        ids.append(submenu.id)
        for id in ids:
            await self.cache.delete(str(id))

    async def update_submenu_cache(self, menu_id: UUID, submenu: SubmenuRead):
        submenu.id = str(submenu.id)
        await self.cache.set(str(submenu.id), await self.deserialize_schema(submenu))
        await self.cache.delete(str(menu_id))
        await self.cache.delete(f'{menu_id}_submenus')
        await self.cache.delete(f'{menu_id}_counts')

    async def get_submenu_list_cache(self, menu_id):
        cached_list = await self.cache.get(f'{menu_id}_submenus')
        if cached_list is None:
            return None
        return [SubmenuRead(**json.loads(submenu)) for submenu in json.loads(cached_list)]


class DishCacheService(CacheService):

    async def get_model_list_cache(self, submenu_id) -> list[DishRead] | None:
        list = await self.cache.get(f'{submenu_id}_dishes')
        if list is None:
            return None
        return [DishRead(**json.loads(dish)) for dish in json.loads(list)]

    async def invalidate_dish_cache(self, key: UUID, submenu_key: UUID, menu_key: UUID) -> None:
        related_keys = [key, submenu_key, menu_key, f'{menu_key}_submenus', f'{menu_key}_counts',
                        f'{submenu_key}_dishes']
        for related_key in related_keys:
            await self.cache.delete(str(related_key))
