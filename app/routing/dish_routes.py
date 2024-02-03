from uuid import UUID

import aioredis
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, get_redis
from app.schemas.dish_schemas import (
    DishCreate,
    DishCreateWithSubmenuId,
    DishIdOnly,
    DishRead,
)
from app.services.dish_services import DishService

dish_router = APIRouter(tags=['dish-routers'])


@dish_router.patch('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}',
                   response_model=DishRead,
                   status_code=200)
async def dish_patch(target_menu_id: UUID,
                     target_submenu_id: UUID,
                     target_dish_id: UUID,
                     dish_update: DishCreate,
                     db: AsyncSession = Depends(get_db),
                     redis: aioredis.Redis = Depends(get_redis)) -> DishRead:
    service = DishService(db, redis)
    dish = await service.patch(target_id=target_dish_id,
                               dish_update=dish_update,
                               target_menu_id=target_menu_id,
                               target_submenu_id=target_submenu_id
                               )
    return dish


@dish_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
                 response_model=list[DishRead],
                 status_code=200,
                 name='dish-list')
async def list_dishes(target_menu_id: UUID,
                      target_submenu_id: UUID,
                      db: AsyncSession = Depends(get_db),
                      redis: aioredis.Redis = Depends(get_redis)) -> list[DishRead]:
    service = DishService(db, redis)
    dishes = await service.read_many(target_id=target_submenu_id)
    return dishes


@dish_router.post('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
                  status_code=201,
                  response_model=DishRead,
                  name='dish-create')
async def dish_create(target_menu_id: UUID,
                      target_submenu_id: UUID,
                      dish_schema: DishCreate,
                      db: AsyncSession = Depends(get_db),
                      redis: aioredis.Redis = Depends(get_redis)) -> DishRead:
    dish_schema = DishCreateWithSubmenuId(**dish_schema.model_dump(),
                                          submenu_id=target_submenu_id)
    service = DishService(db, redis)
    new_dish = await service.create(dish_schema,
                                    target_menu_id,
                                    target_submenu_id)
    return new_dish


@dish_router.delete('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes'
                    '/{target_dish_id}',
                    status_code=200,
                    response_model=DishIdOnly)
async def dish_delete(target_dish_id: UUID,
                      target_submenu_id: UUID,
                      target_menu_id: UUID,
                      db: AsyncSession = Depends(get_db),
                      redis: aioredis.Redis = Depends(get_redis)) -> DishIdOnly:
    service = DishService(db, redis)
    delete_dish = await service.delete(target_id=target_dish_id,
                                       target_submenu_id=target_submenu_id,
                                       target_menu_id=target_menu_id)
    return delete_dish


@dish_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}',
                 status_code=200,
                 response_model=DishRead)
async def dish_read(target_menu_id: UUID,
                    target_submenu_id: UUID,
                    target_dish_id: UUID,
                    db: AsyncSession = Depends(get_db),
                    redis: aioredis.Redis = Depends(get_redis)) -> DishRead:
    service = DishService(db, redis)
    dish = await service.read(target_id=target_dish_id)
    return dish
