from uuid import UUID

import aioredis
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, get_redis
from app.schemas.menu_schemas import MenuCreate, MenuIdOnly, MenuRead, MenuReadCounts
from app.services.menu_services import MenuService

menu_router = APIRouter(tags=['menu-routes'])


@menu_router.get('/menus/{target_menu_id}/counts',
                 status_code=200,
                 response_model=MenuReadCounts,
                 name='menu-read-counts')
async def read_menu_with_counts(target_menu_id: UUID,
                                db: AsyncSession = Depends(get_db),
                                redis: aioredis.Redis = Depends(get_redis)) -> MenuReadCounts:
    service = MenuService(db, redis)
    menu = await service.read_with_counts(target_id=target_menu_id)
    return menu


@menu_router.get('/menus',
                 status_code=200,
                 response_model=list[MenuRead],
                 name='menus-read')
async def read_all_menus(db: AsyncSession = Depends(get_db),
                         redis: aioredis.Redis = Depends(get_redis)) -> list[MenuRead]:
    service = MenuService(db, redis)
    menus = await service.read_many()
    return [menu for menu in menus]


@menu_router.post('/menus',
                  status_code=201,
                  response_model=MenuRead,
                  name='menu-create')
async def menu_create(menu_schema: MenuCreate,
                      db: AsyncSession = Depends(get_db),
                      redis: aioredis.Redis = Depends(get_redis)):
    service = MenuService(db, redis)
    new_menu = await service.create(menu_schema)
    return new_menu


@menu_router.get('/menus/{target_menu_id}',
                 status_code=200,
                 response_model=MenuRead,
                 name='menu-read')
async def menu_read(target_menu_id: UUID,
                    db: AsyncSession = Depends(get_db),
                    redis: aioredis.Redis = Depends(get_redis)) -> MenuRead:
    service = MenuService(db, redis)
    menu = await service.read(target_id=target_menu_id)
    return menu


@menu_router.patch('/menus/{target_menu_id}',
                   status_code=200,
                   response_model=MenuRead,
                   name='menu-patch')
async def menu_patch(target_menu_id: UUID,
                     menu_update: MenuCreate,
                     db: AsyncSession = Depends(get_db),
                     redis: aioredis.Redis = Depends(get_redis)) -> MenuRead:
    service = MenuService(db, redis)
    update_menu = await service.patch(target_id=target_menu_id, menu_update=menu_update)
    return update_menu


@menu_router.delete('/menus/{target_menu_id}',
                    status_code=200,
                    response_model=MenuIdOnly,
                    name='menu-delete')
async def menu_delete(target_menu_id: UUID,
                      db: AsyncSession = Depends(get_db),
                      redis: aioredis.Redis = Depends(get_redis)) -> MenuIdOnly:
    service = MenuService(db, redis)
    delete_menu = await service.delete(target_id=target_menu_id)
    return delete_menu
