from uuid import UUID

from app.db.models import Dish, SubMenu
from app.db.repository.crud import MenuCrud
from app.schemas.dish_schemas import (
    DishCreate,
    DishCreateWithSubmenuId,
    DishIdOnly,
    DishRead,
)
from app.services.cache.cache_service import DishCacheService

from .base import BaseService


class DishService(BaseService):

    def __init__(self, db, redis):
        BaseService.__init__(self, db)
        self.cache = DishCacheService(redis)
        self.database_manager = MenuCrud(self.db)

    async def patch(self,
                    target_id: UUID,
                    target_menu_id,
                    target_submenu_id,
                    dish_update: DishCreate,
                    ) -> DishRead:
        """
        Function takes dish id, submenu id, menu id and update schema, then sends it to database manager and
        deletes cached data with cache manager
        """
        async with self.db as db_session:
            async with db_session.begin():
                update_result = await self.database_manager.update_object(object_class=Dish,
                                                                          object_id=target_id,
                                                                          object_schema=dish_update)
                dish = DishRead(**update_result.__dict__).round_price()

                await self.cache.invalidate_dish_cache(key=target_id,
                                                       menu_key=target_menu_id,
                                                       submenu_key=target_submenu_id)
                await self.cache.set_model_cache(dish.id, dish)
                return dish

    async def read_many(self, target_id: UUID) -> list[DishRead]:
        """
        Function takes submenu id and sends it to cache manager, returns list of dish if value exists in cache,
        otherwise function sends id to database manager, then return list of submenus if are in
        """
        cached = await self.cache.get_model_list_cache(f'{target_id}_dishes', DishRead)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                dishes = await self.database_manager.read_objects(submenu_id=target_id,
                                                                  object_class=Dish,
                                                                  object_name='dish')

                dishes_schemas = [DishRead(**dish.__dict__) for dish in dishes]
                await self.cache.set_list(f'{target_id}_dishes', dishes_schemas)
                return dishes_schemas

    async def create(self,
                     dish_schema: DishCreateWithSubmenuId,
                     target_menu_id: UUID,
                     target_submenu_id: UUID
                     ) -> DishRead:
        """Function takes id and schema of submenu, sends it to cache and database managers, then returns schema"""
        async with self.db as db_session:
            async with db_session.begin():
                new_dish = await self.database_manager.create_object(object_schema=dish_schema,
                                                                     object_class=Dish,
                                                                     parent_id=dish_schema.submenu_id,
                                                                     parent_class=SubMenu)
                new_dish_schema = DishRead(**new_dish.__dict__).round_price()
                await self.cache.invalidate_dish_cache(key=new_dish.id,
                                                       menu_key=target_menu_id,
                                                       submenu_key=target_submenu_id)
                await self.cache.set_model_cache(new_dish.id, new_dish_schema)
                return new_dish_schema

    async def read(self, target_id: UUID) -> DishRead:
        """
        Function takes id and sends it checks if target menu in cache if it is returns cached value
        otherwise firstly gets data from database manager, then saves with cache manager and returns submenu schema
        """
        cached = await self.cache.get_model_cache(target_id, DishRead)
        if cached is not None:
            return cached.round_price()

        async with self.db as db_session:
            async with db_session.begin():
                dish_db = await self.database_manager.read_object(object_id=target_id,
                                                                  object_name='dish',
                                                                  object_class=Dish)
                dish = DishRead(**dish_db.__dict__).round_price()

                await self.cache.set_model_cache(target_id, dish)
                return dish

    async def delete(self,
                     target_id: UUID,
                     target_submenu_id: UUID,
                     target_menu_id: UUID
                     ) -> DishIdOnly:
        """Function takes submenu id and sends it to database manager and deletes cache with cache manager"""
        async with self.db as db_session:
            async with db_session.begin():
                await self.database_manager.delete_object(object_class=Dish,
                                                          object_id=target_id)

                dish_id_only = DishIdOnly(id=target_id)
                await self.cache.invalidate_dish_cache(key=target_id,
                                                       menu_key=target_menu_id,
                                                       submenu_key=target_submenu_id)
                return dish_id_only
