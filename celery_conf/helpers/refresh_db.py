from asyncio import get_event_loop

from aioredis import Redis
from fastapi import BackgroundTasks

from app.db.repository.utils import AdvancedMenuRepository
from app.db.session import async_session, redis_pool
from app.services.task_services.menu_utils import MenuSyncHelper
from app.services.task_services.sales_manager import SalesManager
from app.services.task_services.task import (
    compare_sheet_and_db,
    parse_data,
    prepare_data,
)


class RefreshDatabaseTaskHelper:

    def __init__(self, credentials_path: str, sheet_url: str):
        self.background_tasks = BackgroundTasks()
        self.redis = Redis(connection_pool=redis_pool)
        self.db_manager = AdvancedMenuRepository(async_session())
        self.event_loop = get_event_loop().run_until_complete
        self.credentials_path = credentials_path
        self.sheet_url = sheet_url
        self.sync_helper = MenuSyncHelper(
            self.db_manager,
            self.redis,
            self.background_tasks
        )
        self.sales_manager = SalesManager(self.redis, self.db_manager)

    def make_background_tasks(self):
        self.event_loop(self.background_tasks())

    def parse_sheet_make_objects(self) -> dict[list[dict], list[dict]]:

        parsed_sheet_data = self.event_loop(
            parse_data(self.credentials_path, self.sheet_url)
        )

        menus_and_sales = self.event_loop(
            prepare_data(parsed_sheet_data)
        )

        return menus_and_sales

    def compare_sheet_and_db(
            self,
            parsed_menus: list[dict]
    ) -> dict[list[dict], list[dict]]:
        compared_menus = self.event_loop(compare_sheet_and_db(
            parsed_menus,
            self.db_manager,
            self.redis,
            self.background_tasks)
        )
        return compared_menus

    def synchronize_db_with_sheet(self, compared_menus: dict) -> None:
        self.event_loop(
            self.sync_helper.delete_menus_which_must_not_exist(
                compared_menus['existing_menus'])
        )

        self.event_loop(
            self.sync_helper.populate_menus_which_must_exist(
                compared_menus['menus_to_create'])
        )

        self.make_background_tasks()

    def manage_sales(self, sales: list[dict]) -> None:
        self.make_background_tasks()

        self.event_loop(self.sales_manager.delete_old_sales())
        self.event_loop(self.sales_manager.create_new_sales(sales))
