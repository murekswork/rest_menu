import asyncio

import aioredis
import gspread
from fastapi import BackgroundTasks

from app.db.models import Dish, Menu
from app.db.repository.utils import AdvancedMenuManager
from app.db.session import async_session, redis_pool
from app.schemas.dish_schemas import DishCreateWithSubmenuId
from app.schemas.menu_schemas import MenuCreate
from app.schemas.submenu_schemas import SubmenuCreateWithMenuId

from .cache.cache_service import DishCacheService, MenuCacheService, SubmenuCacheService
from .dish_services import DishService
from .menu_services import MenuService
from .submenu_services import SubmenuService


class TaskService:

    def __init__(self,
                 db=async_session(),
                 redis_cp=redis_pool) -> None:
        self.db = db
        self.redis = aioredis.Redis(connection_pool=redis_cp)
        self.database_manager = AdvancedMenuManager(db_session=self.db)
        self.google_account = gspread.service_account(filename='creds.json')
        self.background_tasks = BackgroundTasks()

    async def get_sheet_data(self) -> list[list]:
        """Method to get sheet data with Google api"""
        sheet = self.google_account.open_by_url(
            'https://docs.google.com/spreadsheets/d/1CSA6u'
            'v3DJa383_CAvknhTmrDbIV3VtSz_WmfcCnFSyw/edit#gid=0')
        worksheet = sheet.get_worksheet(0)
        data = worksheet.get_all_values()
        return data

    @staticmethod
    async def create_objects_from_sheet_rows(table_data: list[list]) -> dict:
        """
        Method takes data from google sheet, iterates through it and fill
        create objects from rows, then return dict with menus and sales
        """
        menus = []
        sales = []
        for row in table_data:
            if row[0]:
                menus.append(
                    {
                        'title': row[1],
                        'description': row[2],
                        'submenus': []
                    }
                )
            elif row[1]:
                menus[-1]['submenus'].append(
                    {
                        'title': row[2],
                        'description': row[3],
                        'dishes': []
                    }
                )
            elif row[2]:
                menus[-1]['submenus'][-1]['dishes'].append(
                    {
                        'title': row[3],
                        'description': row[4],
                        'price': float(row[5].replace(',', '.'))
                    }
                )
            if row[6]:
                sales.append(
                    {'title': row[3], 'description': row[4], 'sale': row[6]})
        return {'menus': menus, 'sales': sales}

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
        new_menu = menu.copy()
        await self.remove_ids_and_change_prices(new_menu)
        return new_menu

    async def delete_menus_which_must_not_exist(self,
                                                correct_menus: list[str]
                                                ) -> None:
        """
        Method takes correct menu ids list and then check each menu id in db if
        its in correct list and deletes all menus from db are not in existing list
        """
        service = MenuService(self.database_manager,
                              cache_manager=MenuCacheService(self.redis))
        db_menus_ids = await self.database_manager.get_all_ids(Menu)
        for menu_id in db_menus_ids:
            if menu_id not in correct_menus:
                await service.delete(menu_id,
                                     background_tasks=self.background_tasks)

    async def populate_menus_which_must_exist(self,
                                              menus_to_be_created: list[dict]
                                              ) -> None:
        """
        This method iterates over each menu in the input list, creates the menu
        in the database, then creates its submenus and dishes if they exist.
        It uses MenuService, SubmenuService, and DishService to interact with
        the database and cache services for creating menus, submenus, and dishes.
        """
        if not menus_to_be_created:
            return None

        menu_service = MenuService(
            self.database_manager, MenuCacheService(self.redis)
        )
        submenu_service = SubmenuService(
            self.database_manager, SubmenuCacheService(self.redis)
        )
        dish_service = DishService(
            self.database_manager, DishCacheService(self.redis)
        )
        for menu in menus_to_be_created:
            new_menu = await menu_service.create(
                MenuCreate(
                    title=menu['title'],
                    description=menu['description']
                ),
                background_tasks=self.background_tasks
            )

            if menu['submenus']:
                for submenu in menu['submenus']:
                    new_submenu = await submenu_service.create(
                        target_menu_id=new_menu.id,
                        submenu_schema=SubmenuCreateWithMenuId(
                            menu_id=new_menu.id,
                            title=submenu['title'],
                            description=submenu['description']
                        ),
                        background_tasks=self.background_tasks
                    )
                    if submenu['dishes']:
                        for dish in submenu['dishes']:
                            await dish_service.create(
                                target_menu_id=new_menu.id,
                                target_submenu_id=new_submenu.id,
                                dish_schema=DishCreateWithSubmenuId(
                                    submenu_id=new_submenu.id,
                                    title=dish['title'],
                                    description=dish['description'],
                                    price=dish['price']
                                ),
                                background_tasks=self.background_tasks
                            )

    async def fill_dish_sales(self, sale_dishes: list[dict]) -> None:
        """
        This method deletes existing sales data and menus from the cache, then
        fills in the sales data for each dish provided in the input list. It
        retrieves the dish ID from the database based on the dish title and
        description, stores the sales data for each dish in a dictionary, and
        updates the cache with the new sales data.
        """
        await self.redis.delete('sales_data', 'menus')
        new_sales_data = {}

        for dish in sale_dishes:
            dish_id = await self.database_manager.read_by_kwargs(
                obj_class=Dish,
                title=dish['title'],
                description=dish['description']
            )
            new_sales_data[f'{dish_id}'] = dish['sale']
            await self.redis.delete(f'{dish_id}')

        await self.redis.set('sales_data', str(new_sales_data))

    async def align_sheet_and_db(self, table_data: dict):
        """
        This method compares menus from the sheet with menus in the database.
        It identifies menus that are equal in both the sheet and the database,
        deletes menus that should not exist in the database, and populates
        menus that should exist but are missing. Finally, it fills in the sales
        data and closes the database connection.
        """
        service = MenuService(self.database_manager,
                              MenuCacheService(self.redis))

        # its list of menus that will be created
        not_existing_lists = table_data['menus'].copy()

        # its list of correct menus which is equal in db and sheets
        menus_which_are_equal_in_db_and_sheet = []

        for menu_sh in table_data['menus']:
            db_menu_id = await self.database_manager.read_by_kwargs(
                obj_class=Menu,
                title=menu_sh['title'],
                description=menu_sh['description']
            )
            # get menu from db, if not - just skip iteration
            if not db_menu_id:
                continue
            try:
                menu = (await service.read(db_menu_id, self.background_tasks)
                        ).model_dump()
                # modify menu for comparing
                menu_db = await self.prepare_menu_for_comparison(menu)

                if menu_db == menu_sh:
                    # loop for compare each menu with value from database
                    # and if its equal remove from not existing list and add to
                    # correct menu id list
                    menus_which_are_equal_in_db_and_sheet.append(
                        str(menu['id']))
                    not_existing_lists.remove(menu_sh)

            except Exception as e:
                print(e)

        await self.delete_menus_which_must_not_exist(
            menus_which_are_equal_in_db_and_sheet)

        await self.populate_menus_which_must_exist(
            not_existing_lists)

        await self.background_tasks()
        await self.fill_dish_sales(table_data['sales'])
        await self.db.close()
