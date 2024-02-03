from uuid import UUID

from app.db.models import Menu
from app.db.repository.crud import MenuCrud
from app.db.repository.utils import MenuUTIL
from app.schemas import dish_schemas, menu_schemas, submenu_schemas
from app.schemas.menu_schemas import MenuRead, MenuReadCounts
from app.services.cache.cache_service import MenuCacheService

from .base import BaseService


class MenuService(BaseService):

    def __init__(self, db, redis):
        BaseService.__init__(self, db)
        self.cache_manager = MenuCacheService(redis)

    async def _read_menu_with_counts(self, target_id: UUID):
        cached = await self.cache_manager.get_model_cache(f'{target_id}_counts', MenuReadCounts)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                menu_util = MenuUTIL(db_session)
                menu = await menu_util.read_menu_with_counts(menu_id=target_id)

                menu_schema = MenuReadCounts(id=menu.id,
                                             title=menu.title,
                                             description=menu.description,
                                             dishes_count=menu.dish_count,
                                             submenus_count=menu.submenu_count)

                await self.cache_manager.set_menu_cache_with_counts(target_id, menu_schema)
                return menu_schema

    async def _read_all_menus(self):
        cached = await self.cache_manager.get_model_list_cache(key='menus', schema=MenuRead)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session)
                menus_db = await menu_dal.read_objects(object_name='menu', object_class=Menu)
                result = []
                for menu in menus_db:
                    menu_schema = menu_schemas.MenuRead(**menu.__dict__)
                    submenus_schemas = []

                    for submenu in menu.submenus:
                        submenu_schema = submenu_schemas.SubmenuRead(**submenu.__dict__)
                        dishes_schemas = [dish_schemas.DishRead(**dish.__dict__).round_price()
                                          for dish in submenu.dishes]
                        submenu_schema.dishes = dishes_schemas
                        submenu_schema.get_dishes_count()
                        submenus_schemas.append(submenu_schema)

                    menu_schema.submenus = submenus_schemas
                    menu_schema.get_counts()
                    result.append(menu_schema)

                await self.cache_manager.set_list('menus', result)
                return result

    async def _menu_create(self, menu_schema: menu_schemas.MenuCreate) -> menu_schemas.MenuRead:
        """Method takes menu schema and sends to database manager"""
        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session)
                new_menu = await menu_dal.create_object(object_class=Menu,
                                                        object_schema=menu_schema)
                menu_schema = MenuRead(**new_menu.__dict__)
                menu_schema.submenus = []
                await self.cache_manager.create_menu_cache(menu_schema.id, menu_schema)
                return menu_schema

    async def _menu_read(self, target_id: UUID) -> menu_schemas.MenuRead:
        """
        Method checks if target id is in cache and returns if it is
        else sends menu id to database controller serializes into pydantic model and returns
        """

        cached = await self.cache_manager.get_model_cache(target_id, MenuRead)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session)
                object_db = await menu_dal.read_object(object_id=target_id,
                                                       object_name='menu',
                                                       object_class=Menu)
                menu_schema = menu_schemas.MenuRead(**object_db.__dict__)
                submenus_schemas = []
                for submenu in object_db.submenus:
                    submenu_schema = submenu_schemas.SubmenuRead(**submenu.__dict__)
                    dishes_schemas = [dish_schemas.DishRead(**dish.__dict__).round_price() for dish in submenu.dishes]
                    submenu_schema.dishes = dishes_schemas
                    submenu_schema.get_dishes_count()
                    submenus_schemas.append(submenu_schema)

                menu_schema.submenus = submenus_schemas
                menu_schema.get_counts()

                await self.cache_manager.set_model_cache(target_id, menu_schema)
                return menu_schema

    async def _menu_delete(self, target_id: UUID) -> menu_schemas.MenuIdOnly:
        """
        Method takes menu id and send it to database manager and cache manager
        then return deleted menu id
        """
        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session)
                menu = await menu_dal.read_object(object_id=target_id, object_name='menu', object_class=Menu)
                await self.cache_manager.invalidate_menu_cache(MenuRead(**menu.__dict__))

                await menu_dal.delete_object(object_class=Menu, object_id=target_id)
                return menu_schemas.MenuIdOnly(menu_id=target_id)

    async def _menu_patch(self, target_id: UUID,
                          menu_update: menu_schemas.MenuCreate) -> menu_schemas.MenuRead:
        """
        Method takes menu id and update schema and send it to database
        also sends menu id to cache manager
        """
        async with self.db as db_session:
            async with db_session.begin():
                menu_dal = MenuCrud(db_session=db_session)
                update_result = await menu_dal.update_object(object_class=Menu,
                                                             object_id=target_id,
                                                             object_schema=menu_update)
                menu_schema = MenuRead(**update_result.__dict__)
                await self.cache_manager.update_menu_cache(target_id, menu_schema)
                return menu_schema
