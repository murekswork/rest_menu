from aioredis import Redis
from celery import Celery
from fastapi import BackgroundTasks

from app.db.repository.utils import AdvancedMenuRepository
from app.db.session import async_session, redis_pool
from app.services.task_services.menu_utils import MenuManager
from app.services.task_services.sales_manager import SalesManager
from app.services.task_services.task import (
    compare_sheet_and_db,
    parse_data,
    prepare_data,
)
from settings import TASK_CREDENTIALS_FILE_PATH, TASK_SHEET_URL

app = Celery('tasks')

# This beat_schedule dictionary creates schedule with task that calls
# function  refresh_db_data every 15 seconds
app.conf.beat_schedule = {
    'run-every-15-seconds':
        {
            'task': 'celery_conf.celery_app.refresh_db_data',
            'schedule': 15.0,
        }
}


@app.task()
def refresh_db_data():
    """
    Refreshes the database data by comparing sheet objects with existing
    database menus, deleting menus that should not exist, and creating new
    menus that should exist. It also deletes old sales data and creates new
    sales data.

    Steps:
    1. Parses data from a Google Spreadsheet using credentials 'from creds.json'
    2. Prepares the parsed data into sheet objects.
    3. Compares sheet objects with existing database menus and retrieves
    menus to create and existing menus.
    4. Deletes menus that should not exist in the database.
    5. Populates menus that should exist in the database.
    6. Deletes old sales data.
    7. Creates new sales data.
    8. Closes the database session.

    Note: The function uses background tasks for asynchronous operations.
    """
    import asyncio
    background_tasks = BackgroundTasks()
    redis = Redis(connection_pool=redis_pool)
    db_manager = AdvancedMenuRepository(async_session())
    loop = asyncio.get_event_loop().run_until_complete

    parsed_data = loop(parse_data(
        TASK_CREDENTIALS_FILE_PATH,
        TASK_SHEET_URL)
    )

    sheet_objects = loop(prepare_data(parsed_data))

    sheet_menus = loop(compare_sheet_and_db(
        sheet_objects['menus'],
        db_manager,
        redis,
        background_tasks)
    )

    sync_manager = MenuManager(db_manager, redis, background_tasks)

    loop(sync_manager.delete_menus_which_must_not_exist(
        sheet_menus['existing_menus'])
    )
    loop(sync_manager.populate_menus_which_must_exist(
        sheet_menus['menus_to_create'])
    )

    sales_manager = SalesManager(redis, db_manager)

    loop(background_tasks())

    loop(sales_manager.delete_old_sales())

    loop(sales_manager.create_new_sales(sheet_objects['sales']))

    loop(db_manager.db_session.close())
