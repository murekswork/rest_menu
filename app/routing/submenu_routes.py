from uuid import UUID

import aioredis
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, get_redis
from app.schemas.errors import DatabaseErrorResponseSchema
from app.schemas.submenu_schemas import (
    SubmenuCreate,
    SubmenuCreateWithMenuId,
    SubmenuIdOnly,
    SubmenuRead,
)
from app.services.submenu_services import SubmenuService

submenu_router = APIRouter(tags=['submenu-router'])


@submenu_router.get('/menus/{target_menu_id}/submenus',
                    status_code=200,
                    response_model=list[SubmenuRead],
                    responses={404: {'description': 'Submenus parent menu not found'}},
                    name='submenu-read-list')
async def submenus_read(
        target_menu_id: UUID,
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
) -> list[SubmenuRead]:

    service = SubmenuService(db, redis)
    submenu_list = await service.read_many(target_menu_id=target_menu_id)
    return submenu_list


@submenu_router.post('/menus/{target_menu_id}/submenus',
                     status_code=201,
                     response_model=SubmenuRead,
                     responses={404: {'description': 'Submenu parent menu not found',
                                      'model': DatabaseErrorResponseSchema}},
                     name='submenu-create')
async def submenu_create(
        target_menu_id: UUID,
        submenu_schema: SubmenuCreate,
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
) -> SubmenuRead:

    submenu_schema_with_menu_id = SubmenuCreateWithMenuId(menu_id=target_menu_id, **submenu_schema.model_dump())
    service = SubmenuService(db, redis)
    new_submenu = await service.create(submenu_schema=submenu_schema_with_menu_id,
                                       target_menu_id=target_menu_id)

    return new_submenu


@submenu_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}',
                    status_code=200,
                    responses={404: {'description': 'Submenu not found',
                                     'model': DatabaseErrorResponseSchema}},
                    response_model=SubmenuRead)
async def submenu_read(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
) -> SubmenuRead:

    service = SubmenuService(db, redis)
    target_submenu = await service.read(target_submenu_id, target_menu_id)
    return target_submenu.get_dishes_count()


@submenu_router.delete('/menus/{target_menu_id}/submenus/{target_submenu_id}',
                       status_code=200,
                       response_model=SubmenuIdOnly,
                       responses={404: {'description': 'Submenu not found',
                                        'model': DatabaseErrorResponseSchema}},
                       name='submenu-delete')
async def submenu_delete(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
) -> SubmenuIdOnly:

    service = SubmenuService(db, redis)
    delete_submenu = await service.delete(target_submenu_id, target_menu_id)
    return delete_submenu


@submenu_router.patch('/menus/{target_menu_id}/submenus/{target_submenu_id}',
                      status_code=200,
                      responses={404: {'description': 'Submenu not found',
                                       'model': DatabaseErrorResponseSchema}},
                      response_model=SubmenuRead)
async def submenu_patch(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        submenu_update: SubmenuCreate,
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
) -> SubmenuRead:

    service = SubmenuService(db, redis)
    submenu = await service.patch(target_submenu_id=target_submenu_id,
                                  target_menu_id=target_menu_id,
                                  submenu_update=submenu_update)
    return submenu
