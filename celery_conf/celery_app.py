from celery import Celery

from celery_conf.helpers.refresh_db import RefreshDatabaseTaskHelper
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


@app.task
def refresh_db_data():
    """
    Refreshes the database data by comparing sheet objects with existing
    database menus, deleting menus that should not exist, and creating new
    menus that should exist. It also deletes old sales data and creates new
    sales data.
    """
    task_helper = RefreshDatabaseTaskHelper(TASK_CREDENTIALS_FILE_PATH,
                                            TASK_SHEET_URL)

    parsed_menus_and_sales = task_helper.parse_sheet_make_objects()

    compared_menus = task_helper.compare_sheet_and_db(
        parsed_menus_and_sales['menus']  # type: ignore
    )

    task_helper.synchronize_db_with_sheet(compared_menus)

    task_helper.manage_sales(parsed_menus_and_sales['sales'])  # type: ignore
