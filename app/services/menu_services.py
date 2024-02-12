from uuid import UUID

from fastapi import BackgroundTasks, Depends

from app.db.models import Menu
from app.db.repository.crud import MenuCrud
from app.schemas.dish_schemas import DishRead
from app.schemas.menu_schemas import (
    MenuCreate,
    MenuIdOnly,
    MenuRead,
    MenuReadCounts
)
from app.schemas.submenu_schemas import SubmenuRead
from app.services.cache.cache_service import MenuCacheService


class MenuService:

    def __init__(self,
                 db: MenuCrud = Depends(),
                 cache_manager: MenuCacheService = Depends()) -> None:
        self.cache_manager = cache_manager
        self.database_manager = db

    async def read_with_counts(self,
                               target_id: UUID,
                               background_tasks: BackgroundTasks
                               ) -> MenuReadCounts:
        """
        Function takes id of menu and firstly checks for cached data and
        returns if it exists, otherwise function send id to class
        method, then save to cache and return it
        """
        cached = await self.cache_manager.get_model_cache(
            f'{target_id}_counts',
            MenuReadCounts
        )
        if cached is not None:
            return cached

        menu = await self.database_manager.read_menu_with_counts(target_id)

        menu_schema = MenuReadCounts(
            id=menu.id,
            title=menu.title,
            description=menu.description,
            dishes_count=menu.dish_count,
            submenus_count=menu.submenu_count
        )
        background_tasks.add_task(
            self.cache_manager.set_menu_cache_with_counts,
            target_id,
            menu_schema
        )
        return menu_schema

    async def read_many(self,
                        background_tasks: BackgroundTasks
                        ) -> list[MenuRead]:
        """
        Method checks for saved cache data and returns if it exists
        return it, otherwise sends id to database manager, then saves
        received data and returns it
        """
        cached = await self.cache_manager.get_model_list_cache(
            key='menus',
            schema=MenuRead
        )
        if cached is not None:
            return cached

        menus_db = await self.database_manager.read_objects(
            object_class=Menu
        )
        result = []
        for menu in menus_db:
            menu_schema = MenuRead(**menu.__dict__)
            submenus_schemas = []

            for submenu in menu.submenus:
                submenu_schema = SubmenuRead(**submenu.__dict__)
                dishes_schemas = [await (DishRead(**dish.__dict__)
                                         .check_sale(self.cache_manager))
                                  for dish in submenu.dishes]
                submenu_schema.dishes = dishes_schemas
                submenu_schema.get_dishes_count()
                submenus_schemas.append(submenu_schema)

            menu_schema.submenus = submenus_schemas
            menu_schema.get_counts()
            result.append(menu_schema)

        background_tasks.add_task(
            self.cache_manager.set_list,
            'menus',
            result
        )
        return result

    async def create(self,
                     menu_schema: MenuCreate,
                     background_tasks: BackgroundTasks
                     ) -> MenuRead:
        """Method takes menu schema and sends to database manager"""
        new_menu = await self.database_manager.create_object(
            object_class=Menu,
            object_schema=menu_schema
        )
        menu_schema = MenuRead(**new_menu.__dict__)
        menu_schema.submenus = []

        background_tasks.add_task(
            self.cache_manager.create_menu_cache,
            menu_schema.id,
            menu_schema
        )
        return menu_schema

    async def read(self,
                   target_id: UUID,
                   background_tasks: BackgroundTasks,
                   _no_cache: bool = False) -> MenuRead:
        """
        Method checks if target id is in cache and returns if it exists
        otherwise sends menu id to database controller serializes into
        pydantic model and returns
        """
        if _no_cache is False:
            cached = await self.cache_manager.get_model_cache(
                target_id,
                MenuRead
            )
            if cached is not None:
                return cached

        object_db = await self.database_manager.read_object(
            object_id=target_id,
            object_class=Menu
        )
        menu_schema = MenuRead(**object_db.__dict__)
        submenus_schemas = []
        for submenu in object_db.submenus:
            submenu_schema = SubmenuRead(**submenu.__dict__)
            # if __no_cache is true then this called from celery task, so no
            # need to verify available sale
            if _no_cache is False:
                dishes_schemas = [await (DishRead(**dish.__dict__)
                                         .check_sale(self.cache_manager))
                                  for dish in submenu.dishes]
            else:
                dishes_schemas = [DishRead(**dish.__dict__)
                                  for dish in submenu.dishes]

            submenu_schema.dishes = dishes_schemas
            submenu_schema.get_dishes_count()
            submenus_schemas.append(submenu_schema)

        menu_schema.submenus = submenus_schemas
        menu_schema.get_counts()

        if _no_cache is False:
            background_tasks.add_task(
                self.cache_manager.set_model_cache,
                target_id,
                menu_schema
            )
        return menu_schema

    async def delete(self,
                     target_id: UUID | str,
                     background_tasks: BackgroundTasks
                     ) -> MenuIdOnly:
        """
        Function takes menu id and send it to database manager and deletes
        cache with cache manager then returns deleted menu id
        """
        menu = await self.database_manager.read_object(
            object_class=Menu,
            object_id=target_id
        )
        background_tasks.add_task(
            self.cache_manager.invalidate_menu_cache,
            MenuRead(**menu.__dict__)
        )
        await self.database_manager.delete_object(
            object_class=Menu,
            object_id=target_id
        )
        return MenuIdOnly(menu_id=target_id)

    async def patch(self,
                    target_id: UUID,
                    menu_update: MenuCreate,
                    background_tasks: BackgroundTasks
                    ) -> MenuRead:
        """
        Method takes menu id and update schema and send it to database
        also sends menu id to cache manager
        """
        update_result = await self.database_manager.update_object(
            object_class=Menu,
            object_id=target_id,
            object_schema=menu_update
        )
        menu_schema = MenuRead(**update_result.__dict__)
        background_tasks.add_task(
            self.cache_manager.update_menu_cache,
            target_id,
            menu_schema
        )
        return menu_schema
