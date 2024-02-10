import logging

from celery import Celery

from app.services.task_services import TaskService

app = Celery('tasks')
app.autodiscover_tasks()

# This dictionary creates task that calls
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
    Asynchronous Celery task to refresh database data from a sheet.
    This task utilizes asyncio for running asynchronous operations and
    interacts with a TaskService instance to handle the synchronization process
    between a sheet and the database.
    """
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        loop = loop.run_until_complete
        service = TaskService()

        sheet_data = loop(service.get_sheet_data())
        objects = loop(service.create_objects_from_sheet_rows(sheet_data))
        loop(service.align_sheet_and_db(objects))
        logging.warning('Task completed successfully!')

    except Exception as e:
        logging.critical(f'!! Task could not complete successfully !! {e}')
