from uuid import UUID

from fastapi import BackgroundTasks, Depends

from app.db.models import Dish, SubMenu
from app.db.repository.crud import MenuCrud
from app.schemas.dish_schemas import (
    DishCreate,
    DishCreateWithSubmenuId,
    DishIdOnly,
    DishRead,
)
from app.services.cache.cache_service import DishCacheService


class DishService:

    def __init__(self,
                 db: MenuCrud = Depends(),
                 cache: DishCacheService = Depends()
                 ) -> None:
        self.cache = cache
        self.database_manager = db

    async def patch(self,
                    target_id: UUID,
                    target_menu_id,
                    target_submenu_id,
                    dish_update: DishCreate,
                    background_tasks: BackgroundTasks) -> DishRead:
        """
        Method takes dish id, submenu id, menu id and update schema, then
        sends it to database manager and deletes cached data with cache manager
        """

        update_result = await self.database_manager.update_object(
            object_class=Dish,
            object_id=target_id,
            object_schema=dish_update
        )
        dish = DishRead(**update_result.__dict__).round_price()

        background_tasks.add_task(
            self.cache.invalidate_dish_cache,
            key=target_id,
            menu_key=target_menu_id,
            submenu_key=target_submenu_id
        )
        background_tasks.add_task(
            self.cache.set_model_cache,
            dish.id,
            dish
        )
        return dish

    async def read_many(self, target_id: UUID,
                        background_tasks: BackgroundTasks) -> list[DishRead]:
        """
        Method takes submenu id and sends it to cache manager, returns list
        of dish if value exists in cache, otherwise function sends id to
        database manager, then return list of submenus if are in
        """
        cached = await self.cache.get_model_list_cache(
            f'{target_id}_dishes',
            DishRead
        )
        if cached is not None:
            return cached

        dishes = await self.database_manager.read_objects(
            object_class=Dish,
            submenu_id=target_id
        )
        dishes_schemas = [await (DishRead(**dish.__dict__)
                                 .check_sale(self.cache))
                          for dish in dishes]
        background_tasks.add_task(
            self.cache.set_list,
            f'{target_id}_dishes',
            dishes_schemas
        )
        return dishes_schemas

    async def create(self,
                     dish_schema: DishCreateWithSubmenuId,
                     target_menu_id: UUID | str,
                     target_submenu_id: UUID | str,
                     background_tasks: BackgroundTasks
                     ) -> DishRead:
        """
        Method takes id and schema of submenu, sends it to cache and
        database managers, then returns schema
        """
        new_dish = await self.database_manager.create_object(
            object_schema=dish_schema,
            object_class=Dish,
            parent_id=dish_schema.submenu_id,
            parent_class=SubMenu
        )
        new_dish_schema = await DishRead(**new_dish.__dict__).check_sale(
            self.cache)

        background_tasks.add_task(
            self.cache.invalidate_dish_cache,
            key=new_dish.id,
            menu_key=target_menu_id,
            submenu_key=target_submenu_id
        )
        background_tasks.add_task(
            self.cache.set_model_cache,
            new_dish.id,
            new_dish_schema
        )
        return new_dish_schema

    async def read(self, target_id: UUID,
                   background_tasks: BackgroundTasks) -> DishRead:
        """
        Method takes id and sends it checks if target menu in cache if it is
        returns cached value otherwise firstly gets data from database manager,
         then saves with cache manager and returns submenu schema
        """
        cached = await self.cache.get_model_cache(
            target_id,
            DishRead
        )
        if cached is not None:
            return cached.round_price()

        dish_db = await self.database_manager.read_object(
            object_id=target_id,
            object_class=Dish
        )
        dish = await DishRead(**dish_db.__dict__).check_sale(self.cache)

        background_tasks.add_task(
            self.cache.set_model_cache,
            target_id,
            dish
        )
        return dish

    async def delete(self,
                     target_id: UUID,
                     target_submenu_id: UUID,
                     target_menu_id: UUID,
                     background_tasks: BackgroundTasks
                     ) -> DishIdOnly:
        """
        Method takes submenu id and sends it to database manager and deletes
        cache with cache manager
        """
        await self.database_manager.delete_object(
            object_class=Dish,
            object_id=target_id
        )
        dish_id_only = DishIdOnly(id=target_id)

        background_tasks.add_task(
            self.cache.invalidate_dish_cache,
            key=target_id,
            menu_key=target_menu_id,
            submenu_key=target_submenu_id
        )
        return dish_id_only
