from uuid import UUID

from app.db.models import Menu, SubMenu
from app.db.repository.crud import MenuCrud
from app.schemas.dish_schemas import DishRead
from app.schemas.submenu_schemas import (
    SubmenuCreate,
    SubmenuCreateWithMenuId,
    SubmenuIdOnly,
    SubmenuRead,
)
from app.services.cache.cache_service import SubmenuCacheService

from .base import BaseService


class SubmenuService(BaseService):

    def __init__(self, db, redis):
        BaseService.__init__(self, db)
        self.cache_manager = SubmenuCacheService(redis)
        self.database_manager = MenuCrud(self.db)

    async def read_many(self, target_menu_id: UUID) -> list[SubmenuRead]:
        """
        Function takes menu id and sends it to cache manager, returns list of submenus if are in
        otherwise function sends id to database manager, then return list of submenus if are in
        """
        cached = await self.cache_manager.get_model_list_cache(f'{target_menu_id}_submenus', SubmenuRead)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                menu_db = await self.database_manager.read_object(object_id=target_menu_id,
                                                                  object_class=Menu)
                submenus_schemas = []
                for submenu in menu_db.submenus:
                    submenu_schema = SubmenuRead(**submenu.__dict__)
                    dishes_schemas = [DishRead(**dish.__dict__).round_price() for dish in submenu.dishes]
                    submenu_schema.dishes = dishes_schemas
                    submenu_schema.get_dishes_count()
                    submenus_schemas.append(submenu_schema)

                await self.cache_manager.set_list(f'{target_menu_id}_submenus', submenus_schemas)
                return submenus_schemas

    async def create(self,
                     submenu_schema: SubmenuCreateWithMenuId,
                     target_menu_id: UUID) -> SubmenuRead:
        """function takes id and schema of submenu, sends it to cache and database managers, then returns schema"""
        async with self.db as db_session:
            async with db_session.begin():
                new_submenu = await self.database_manager.create_object(object_class=SubMenu,
                                                                        object_schema=submenu_schema,
                                                                        parent_id=submenu_schema.menu_id,
                                                                        parent_class=Menu)

                await self.cache_manager.update_submenu_cache(target_menu_id,
                                                              SubmenuRead(**new_submenu.__dict__))
                return SubmenuRead(**new_submenu.__dict__)

    async def read(self,
                   target_submenu_id: UUID,
                   target_menu_id: UUID) -> SubmenuRead:
        """
        Function takes id and sends it checks if target menu in cache if it is returns cached value
        otherwise firstly gets data from database manager, then saves with cache manager and returns submenu schema
        """
        cached = await self.cache_manager.get_model_cache(target_submenu_id, SubmenuRead)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                target_submenu = await self.database_manager.read_object(object_id=target_submenu_id,
                                                                         object_class=SubMenu)
                submenu_schema = SubmenuRead(**target_submenu.__dict__)
                submenu_schema.dishes = [DishRead(**dish.__dict__) for dish in target_submenu.dishes]

                await self.cache_manager.set_model_cache(target_menu_id, submenu_schema)
                return submenu_schema

    async def delete(self, target_submenu_id: UUID, target_menu_id) -> SubmenuIdOnly:
        """Function takes submenu id and sends it to database manager and deletes cache with cache manager"""
        async with self.db as db_session:
            async with db_session.begin():
                submenu = await self.database_manager.read_object(object_id=target_submenu_id,
                                                                  object_class=SubMenu)
                await self.database_manager.delete_object(object_id=target_submenu_id, object_class=SubMenu)

                await self.cache_manager.invalidate_submenu_cache(SubmenuRead(**submenu.__dict__), target_menu_id)
                return SubmenuIdOnly(submenu_id=target_submenu_id)

    async def patch(self,
                    target_submenu_id: UUID,
                    target_menu_id: UUID,
                    submenu_update: SubmenuCreate
                    ) -> SubmenuRead:
        """
        Function takes submenu id, menu id and update schema, then sends it to database manager and
        deletes cached data with cache manager
        """
        async with self.db as db_session:
            async with db_session.begin():
                update_result = await self.database_manager.update_object(object_class=SubMenu,
                                                                          object_id=target_submenu_id,
                                                                          object_schema=submenu_update)
                update_schema = SubmenuRead(**update_result.__dict__)
                await self.cache_manager.update_submenu_cache(target_menu_id, update_schema)
                return update_schema
