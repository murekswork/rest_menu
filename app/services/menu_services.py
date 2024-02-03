from uuid import UUID

from app.db.models import Menu
from app.db.repository.crud import MenuCrud
from app.db.repository.utils import MenuUTIL
from app.schemas.dish_schemas import DishRead
from app.schemas.menu_schemas import MenuCreate, MenuIdOnly, MenuRead, MenuReadCounts
from app.schemas.submenu_schemas import SubmenuRead
from app.services.cache.cache_service import MenuCacheService

from .base import BaseService


class MenuService(BaseService):

    def __init__(self, db, redis) -> None:
        BaseService.__init__(self, db)
        self.cache_manager = MenuCacheService(redis)
        self.database_manager = MenuCrud(self.db)

    async def read_with_counts(self, target_id: UUID) -> MenuReadCounts:
        """
        Function takes id of menu and firstly checks for cached data and returns if it exists,
        otherwise function send id to MenuUtil class method, then save to cache and return it
        """
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

    async def read_many(self) -> list[MenuRead]:
        """
        Function checks for saved cache data and returns if it exists return it,
        otherwise sends id to database manager, then saves received data and returns it
        """
        cached = await self.cache_manager.get_model_list_cache(key='menus', schema=MenuRead)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                menus_db = await self.database_manager.read_objects(object_class=Menu)
                result = []
                for menu in menus_db:
                    menu_schema = MenuRead(**menu.__dict__)
                    submenus_schemas = []

                    for submenu in menu.submenus:
                        submenu_schema = SubmenuRead(**submenu.__dict__)
                        dishes_schemas = [DishRead(**dish.__dict__).round_price()
                                          for dish in submenu.dishes]
                        submenu_schema.dishes = dishes_schemas
                        submenu_schema.get_dishes_count()
                        submenus_schemas.append(submenu_schema)

                    menu_schema.submenus = submenus_schemas
                    menu_schema.get_counts()
                    result.append(menu_schema)

                await self.cache_manager.set_list('menus', result)
                return result

    async def create(self, menu_schema: MenuCreate) -> MenuRead:
        """Method takes menu schema and sends to database manager"""
        async with self.db as db_session:
            async with db_session.begin():
                new_menu = await self.database_manager.create_object(object_class=Menu,
                                                                     object_schema=menu_schema)
                menu_schema = MenuRead(**new_menu.__dict__)
                menu_schema.submenus = []
                await self.cache_manager.create_menu_cache(menu_schema.id, menu_schema)
                return menu_schema

    async def read(self, target_id: UUID) -> MenuRead:
        """
        Method checks if target id is in cache and returns if it exists otherwise
        sends menu id to database controller serializes into pydantic model and returns
        """

        cached = await self.cache_manager.get_model_cache(target_id, MenuRead)
        if cached is not None:
            return cached

        async with self.db as db_session:
            async with db_session.begin():
                object_db = await self.database_manager.read_object(object_id=target_id,
                                                                    object_class=Menu)
                menu_schema = MenuRead(**object_db.__dict__)
                submenus_schemas = []
                for submenu in object_db.submenus:
                    submenu_schema = SubmenuRead(**submenu.__dict__)
                    dishes_schemas = [DishRead(**dish.__dict__).round_price() for dish in submenu.dishes]
                    submenu_schema.dishes = dishes_schemas
                    submenu_schema.get_dishes_count()
                    submenus_schemas.append(submenu_schema)

                menu_schema.submenus = submenus_schemas
                menu_schema.get_counts()

                await self.cache_manager.set_model_cache(target_id, menu_schema)
                return menu_schema

    async def delete(self, target_id: UUID) -> MenuIdOnly:
        """
        Function takes menu id and send it to database manager and deletes cache with cache manager
        then returns deleted menu id
        """
        async with self.db as db_session:
            async with db_session.begin():
                menu = await self.database_manager.read_object(object_id=target_id,
                                                               object_class=Menu)
                await self.cache_manager.invalidate_menu_cache(MenuRead(**menu.__dict__))

                await self.database_manager.delete_object(object_class=Menu, object_id=target_id)
                return MenuIdOnly(menu_id=target_id)

    async def patch(self,
                    target_id: UUID,
                    menu_update: MenuCreate) -> MenuRead:
        """
        Method takes menu id and update schema and send it to database
        also sends menu id to cache manager
        """
        async with self.db as db_session:
            async with db_session.begin():
                update_result = await self.database_manager.update_object(object_class=Menu,
                                                                          object_id=target_id,
                                                                          object_schema=menu_update)
                menu_schema = MenuRead(**update_result.__dict__)
                await self.cache_manager.update_menu_cache(target_id, menu_schema)
                return menu_schema
