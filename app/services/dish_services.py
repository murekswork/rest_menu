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

    async def _dish_patch(self,
                          target_id: UUID,
                          target_menu_id,
                          target_submenu_id,
                          dish_update: DishCreate,
                          ) -> DishRead:
        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session=db_session)
                update_result = await menu_dal.update_object(object_class=Dish,
                                                             object_id=target_id,
                                                             object_schema=dish_update)
                dish = DishRead(**update_result.__dict__).round_price()

                await self.cache.invalidate_dish_cache(key=target_id,
                                                       menu_key=target_menu_id,
                                                       submenu_key=target_submenu_id)
                await self.cache.set_model_cache(dish.id, dish)
                return dish

    async def _list_dishes(self, target_id: UUID) -> list[DishRead]:
        cached = await self.cache.get_model_list_cache(f'{target_id}_dishes', DishRead)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session=db_session)
                dishes = await menu_dal.read_objects(submenu_id=target_id,
                                                     object_class=Dish,
                                                     object_name='dish')

                dishes_schemas = [DishRead(**dish.__dict__) for dish in dishes]
                await self.cache.set_list(f'{target_id}_dishes', dishes_schemas)
                return dishes_schemas

    async def _dish_create(self,
                           dish_schema: DishCreateWithSubmenuId,
                           target_menu_id: UUID,
                           target_submenu_id: UUID) -> DishRead:
        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session=db_session)
                new_dish = await menu_dal.create_object(object_schema=dish_schema,
                                                        object_class=Dish,
                                                        parent_id=dish_schema.submenu_id,
                                                        parent_class=SubMenu)
                new_dish_schema = DishRead(**new_dish.__dict__).round_price()
                await self.cache.invalidate_dish_cache(key=new_dish.id,
                                                       menu_key=target_menu_id,
                                                       submenu_key=target_submenu_id)
                await self.cache.set_model_cache(new_dish.id, new_dish_schema)
                return new_dish_schema

    async def _dish_read(self, target_id: UUID) -> DishRead:
        cached = await self.cache.get_model_cache(target_id, DishRead)
        if cached is not None:
            return cached.round_price()

        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session=db_session)
                object_db = await menu_dal.read_object(object_id=target_id, object_name='dish', object_class=Dish)
                dish = DishRead(**object_db.__dict__).round_price()

                await self.cache.set_model_cache(target_id, dish)
                return dish

    async def _dish_delete(self,
                           target_id: UUID,
                           target_submenu_id: UUID,
                           target_menu_id: UUID) -> DishIdOnly:
        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session=db_session)
                await menu_dal.delete_object(object_class=Dish,
                                             object_id=target_id)

                dish_id_only = DishIdOnly(id=target_id)
                await self.cache.invalidate_dish_cache(key=target_id,
                                                       menu_key=target_menu_id,
                                                       submenu_key=target_submenu_id)
                return dish_id_only
