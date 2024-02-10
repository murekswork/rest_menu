from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.schemas.errors import DatabaseErrorResponseSchema
from app.schemas.menu_schemas import MenuCreate, MenuIdOnly, MenuRead, MenuReadCounts
from app.services.menu_services import MenuService

menu_router = APIRouter(tags=['menu-router'])


@menu_router.get(
    '/menus/{target_menu_id}/counts',
    status_code=200,
    response_model=MenuReadCounts,
    responses={404: {'description': 'Menu not found',
                     'model': DatabaseErrorResponseSchema}},
    name='menu-read-counts')
async def read_menu_with_counts(
        target_menu_id: UUID,
        background_tasks: BackgroundTasks,
        service: MenuService = Depends(),
) -> MenuReadCounts:
    menu = await service.read_with_counts(target_menu_id, background_tasks)
    return menu


@menu_router.get(
    '/menus',
    status_code=200,
    response_model=list[MenuRead],
    name='menus-read')
async def read_all_menus(
        background_tasks: BackgroundTasks,
        service: MenuService = Depends(),
) -> list[MenuRead]:
    menus = await service.read_many(background_tasks)
    return [menu for menu in menus]


@menu_router.post(
    '/menus',
    status_code=201,
    response_model=MenuRead,
    name='menu-create'
)
async def menu_create(
        background_tasks: BackgroundTasks,
        menu_schema: MenuCreate,
        service: MenuService = Depends(),
) -> MenuRead:
    new_menu = await service.create(menu_schema,
                                    background_tasks)
    return new_menu


@menu_router.get(
    '/menus/{target_menu_id}',
    status_code=200,
    response_model=MenuRead,
    responses={404: {'description': 'Menu not found',
                     'model': DatabaseErrorResponseSchema}},
    name='menu-read')
async def menu_read(
        target_menu_id: UUID,
        background_tasks: BackgroundTasks,
        service: MenuService = Depends(),
) -> MenuRead:
    menu = await service.read(target_menu_id, background_tasks)
    return menu


@menu_router.patch(
    '/menus/{target_menu_id}',
    status_code=200,
    response_model=MenuRead,
    responses={404: {'description': 'Menu not found',
                     'model': DatabaseErrorResponseSchema}},
    name='menu-patch')
async def menu_patch(
        target_menu_id: UUID,
        menu_update: MenuCreate,
        background_tasks: BackgroundTasks,
        service: MenuService = Depends(),
) -> MenuRead:
    update_menu = await service.patch(
        target_id=target_menu_id,
        menu_update=menu_update,
        background_tasks=background_tasks)
    return update_menu


@menu_router.delete(
    '/menus/{target_menu_id}',
    status_code=200,
    response_model=MenuIdOnly,
    responses={404: {'description': 'Menu not found',
                     'model': DatabaseErrorResponseSchema}},
    name='menu-delete')
async def menu_delete(
        target_menu_id: UUID,
        background_tasks: BackgroundTasks,
        service: MenuService = Depends(),
) -> MenuIdOnly:
    delete_menu = await service.delete(target_id=target_menu_id,
                                       background_tasks=background_tasks)
    return delete_menu
