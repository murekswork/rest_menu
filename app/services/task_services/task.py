import logging

from fastapi import BackgroundTasks

from app.db.models import Menu
from app.services.menu_services import MenuService

from .menu_utils import MenuModifier
from .sheet_deserialization_service import SheetDeserializationService
from .sheet_parsing_service import SheetParsingInterface


async def parse_data(creds_path: str, url: str):
    """
    Function takes path to credentials file and url for sheet, then authenticates
    user with giver credentials and return parsed data
    """
    parser = SheetParsingInterface()
    await parser.authenticate(creds_path)
    data = await parser.parse_sheet(url)
    return data


async def prepare_data(sheet_data: list[list]) -> dict[list[dict], list[dict]]:
    """
    Function takes sheet data and makes dict of menus and sales
    """
    interface = SheetDeserializationService()
    objects = await interface.create_objects_from_sheet_rows(sheet_data)
    return objects


async def prepare_menu_for_comparison(menu):
    """
    Function takes specific menu from database then call create menu modifier
    class and call prepare_menu_for_comparison method and returns modified menu
    """
    interface = MenuModifier()
    await interface.prepare_menu_for_comparison(menu)
    return menu


async def compare_sheet_and_db(sheet_objects: list,
                               db_manager,
                               cache_manager,
                               background_tasks: BackgroundTasks):
    """
    This function iterates over list with menus from sheet and compares each
    menu against existing  values in database, then fill 2 lists:
    1. Existing menus list is filled with the ids of menus which are both in
    database and in the sheet
    2. Menus to create list is filled when object from sheet has no appropriate
    value in database
    """
    menu_service = MenuService(db_manager, cache_manager)

    existing_menus = []
    menus_to_create = sheet_objects.copy()

    for menu_sheet in sheet_objects:

        db_menu_id = await db_manager.read_by_kwargs(
            Menu,
            menu_sheet['title'],
            menu_sheet['description']
        )
        if not db_menu_id:
            continue

        try:
            menu_schema = (await menu_service.read(
                target_id=db_menu_id,
                background_tasks=background_tasks,
                _no_cache=True
            )).model_dump()
            menu_db = await prepare_menu_for_comparison(menu_schema.copy())

            if menu_sheet == menu_db:
                logging.warning('Found equal menus!')
                existing_menus.append(str(menu_schema['id']))
                menus_to_create.remove(menu_sheet)
            else:
                logging.warning('Found not equal menus!')
        except Exception as e:
            logging.warning(f'Error reading menu with service ! {e}')

    return {'menus_to_create': menus_to_create,
            'existing_menus': existing_menus}
