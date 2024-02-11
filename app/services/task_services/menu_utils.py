import asyncio
import logging

from fastapi import BackgroundTasks

from app.db.models import Menu
from app.schemas.dish_schemas import DishCreateWithSubmenuId
from app.schemas.menu_schemas import MenuCreate
from app.schemas.submenu_schemas import SubmenuCreateWithMenuId
from app.services.cache.cache_service import (
    DishCacheService,
    MenuCacheService,
    SubmenuCacheService,
)
from app.services.dish_services import DishService
from app.services.menu_services import MenuService
from app.services.submenu_services import SubmenuService


class MenuManager:

    def __init__(self,
                 database_manager,
                 redis,
                 background_tasks: BackgroundTasks):

        self.database_manager = database_manager
        self.redis = redis
        self.background_tasks = background_tasks

        self.MenuService = MenuService(self.database_manager,
                                       MenuCacheService(self.redis))

        self.SubmenuService = SubmenuService(self.database_manager,
                                             SubmenuCacheService(self.redis))

        self.DishService = DishService(self.database_manager,
                                       DishCacheService(self.redis))

    async def delete_menus_which_must_not_exist(self, correct_menus):
        """
        Deletes menus from the database that are not in the correct_menus list.
        """
        db_menus_ids = await self.database_manager.get_all_ids(Menu)

        for menu_id in db_menus_ids:
            if menu_id not in correct_menus:
                await self.MenuService.delete(menu_id,
                                              self.background_tasks)
        await self.background_tasks()

    async def populate_menus_which_must_exist(self, menus_to_be_created: list):
        """
        If the list of correct_menus is empty, the method returns None.
        For each menu in the correct_menus list, the method attempts to create
        the menu and its submenus. After creating all menus and submenus, the
        method triggers any background tasks that need to be executed.
        """
        if not menus_to_be_created:
            return None

        for menu in menus_to_be_created:
            logging.warning(f'Trying to populate menu {menu}')
            new_menu = await self.create_menu(menu)
            await self.create_submenus(new_menu, menu['submenus'])
        await self.background_tasks()

    async def create_menu(self, menu_data):
        """Create specific menu in database"""
        new_menu = await self.MenuService.create(
            MenuCreate(title=menu_data['title'],
                       description=menu_data['description']),
            background_tasks=self.background_tasks)
        return new_menu

    async def create_submenus(self, menu, submenus_data):
        """Create specific submenu and dishes if it has in database"""
        if not submenus_data:
            return

        for submenu_data in submenus_data:
            new_submenu = await self.create_submenu(menu, submenu_data)
            await self.create_dishes(menu, new_submenu, submenu_data['dishes'])

    async def create_submenu(self, menu, submenu_data):
        """Create specific submenu in database"""
        new_submenu = await self.SubmenuService.create(
            target_menu_id=menu.id,
            submenu_schema=SubmenuCreateWithMenuId(
                menu_id=menu.id,
                title=submenu_data['title'],
                description=submenu_data['description']),
            background_tasks=self.background_tasks)
        return new_submenu

    async def create_dishes(self, menu, submenu, dishes_data):
        """Create submenus dishes in database"""
        if not dishes_data:
            return

        for dish_data in dishes_data:
            await self.DishService.create(
                target_menu_id=menu.id,
                target_submenu_id=submenu.id,
                dish_schema=DishCreateWithSubmenuId(
                    submenu_id=submenu.id,
                    title=dish_data['title'],
                    description=dish_data['description'],
                    price=dish_data['price']),
                background_tasks=self.background_tasks)


class MenuModifier:

    async def remove_ids_and_change_prices(self, obj):
        """
        Method removes id fields from menu and its sub objects,
        and converts dishes prices to float for future comparison
        """
        if isinstance(obj, dict):
            for key in list(obj.keys()):
                if key == 'id' or key == 'dishes_count' or key == 'submenus_count':
                    del obj[key]
                elif key == 'price':
                    obj[key] = float(obj[key])
                else:
                    await self.remove_ids_and_change_prices(obj[key])
        elif isinstance(obj, list):
            await asyncio.gather(
                *(self.remove_ids_and_change_prices(item) for item in obj))

    async def prepare_menu_for_comparison(self, menu):
        """Method takes makes it copy and sends to remove_id_fields method"""
        await self.remove_ids_and_change_prices(menu)
        return menu
