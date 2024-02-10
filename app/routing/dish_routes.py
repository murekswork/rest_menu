from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.schemas.dish_schemas import (
    DishCreate,
    DishCreateWithSubmenuId,
    DishIdOnly,
    DishRead,
)
from app.schemas.errors import DatabaseErrorResponseSchema
from app.services.dish_services import DishService

dish_router = APIRouter(tags=['dish-router'])


@dish_router.patch(
    '/menus/{target_menu_id}/submenus/'
    '{target_submenu_id}/dishes/{target_dish_id}',
    response_model=DishRead,
    responses={404: {'description': 'Dish not found',
                     'model': DatabaseErrorResponseSchema}},
    status_code=200)
async def dish_patch(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        dish_update: DishCreate,
        background_tasks: BackgroundTasks,
        service: DishService = Depends(),
) -> DishRead:
    dish = await service.patch(target_dish_id,
                               target_menu_id,
                               target_submenu_id,
                               dish_update,
                               background_tasks)
    return dish


@dish_router.get(
    '/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
    response_model=list[DishRead],
    responses={404: {'description': 'Dish not found',
                     'model': DatabaseErrorResponseSchema}},
    status_code=200,
    name='dish-list')
async def list_dishes(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        background_tasks: BackgroundTasks,
        service: DishService = Depends(),
) -> list[DishRead]:
    dishes = await service.read_many(target_submenu_id,
                                     background_tasks)
    return dishes


@dish_router.post(
    '/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
    status_code=201,
    responses={404: {'description': 'Dish parent Submenu not found',
                     'model': DatabaseErrorResponseSchema}},
    response_model=DishRead,
    name='dish-create')
async def dish_create(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        dish_schema: DishCreate,
        background_tasks: BackgroundTasks,
        service: DishService = Depends()
) -> DishRead:
    dish_schema = DishCreateWithSubmenuId(**dish_schema.model_dump(),
                                          submenu_id=target_submenu_id)
    new_dish = await service.create(dish_schema,
                                    target_menu_id,
                                    target_submenu_id,
                                    background_tasks)
    return new_dish


@dish_router.delete(
    '/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes'
    '/{target_dish_id}',
    status_code=200,
    responses={404: {'description': 'Dish not found',
                     'model': DatabaseErrorResponseSchema}},
    response_model=DishIdOnly)
async def dish_delete(
        target_dish_id: UUID,
        target_submenu_id: UUID,
        target_menu_id: UUID,
        background_tasks: BackgroundTasks,
        service: DishService = Depends()
) -> DishIdOnly:
    delete_dish = await service.delete(target_dish_id,
                                       target_submenu_id,
                                       target_menu_id,
                                       background_tasks)
    return delete_dish


@dish_router.get(
    '/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}',
    status_code=200,
    responses={404: {'description': 'Dish not found',
                     'model': DatabaseErrorResponseSchema}},
    response_model=DishRead)
async def dish_read(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        background_tasks: BackgroundTasks,
        service: DishService = Depends()
) -> DishRead:
    dish = await service.read(target_dish_id,
                              background_tasks)
    return dish
