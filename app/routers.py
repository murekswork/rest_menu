import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.schemas import SubmenuRead, DishRead
from db.models import Dish, Menu, SubMenu
from db.session import get_db
from app import schemas
from db.crud import MenuDAL

main_router = APIRouter()


@main_router.get("/menus", response_model=List[schemas.MenuRead])
async def read_all_menus(db: AsyncSession = Depends(get_db)):
    menus = await _read_all_menus(db)
    return [menu for menu in menus]

async def _read_all_menus(db: AsyncSession):
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session)
            menus_db = await menu_dal.read_objects(object_name='menu', object_class=Menu)
            result = []
            for menu in menus_db:
                menu_schema = schemas.MenuRead(**menu.__dict__)
                submenus_schemas = []

                for submenu in menu.submenus:
                    submenu_schema = schemas.SubmenuRead(**submenu.__dict__)
                    dish_schemas = [schemas.DishRead(**dish.__dict__).round_price() for dish in submenu.dishes]
                    submenu_schema.dishes = dish_schemas
                    submenu_schema.get_dishes_count()
                    submenus_schemas.append(submenu_schema)

                menu_schema.submenus = submenus_schemas
                menu_schema.get_counts()
                result.append(menu_schema)
            return result


@main_router.post('/menus', status_code=201, response_model=schemas.MenuRead)
async def menu_create(menu: schemas.MenuCreate, db: AsyncSession = Depends(get_db)):
    new_menu = await _menu_create(menu, db)
    return new_menu

async def _menu_create(menu: schemas.MenuCreate, db: AsyncSession) -> schemas.MenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            new_menu = await menu_dal.create_menu(menu)
            return schemas.MenuRead(**new_menu.__dict__)


@main_router.get('/menus/{target_menu_id}', response_model=schemas.MenuRead)
async def menu_read(target_menu_id: UUID, db: AsyncSession = Depends(get_db)):
    menu = await _menu_read(target_id=target_menu_id, db=db)
    return menu

async def _menu_read(target_id: UUID, db: AsyncSession) -> schemas.MenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            menu_db = await menu_dal.read_object(object_id=target_id, object_name='menu', object_class=Menu)
            menu_schema = schemas.MenuRead(**menu_db.__dict__)
            submenus_schemas = []
            for submenu in menu_db.submenus:
                submenu_schema = schemas.SubmenuRead(**submenu.__dict__)
                dish_schemas = [schemas.DishRead(**dish.__dict__).round_price() for dish in submenu.dishes]
                submenu_schema.dishes = dish_schemas
                submenu_schema.get_dishes_count()
                submenus_schemas.append(submenu_schema)

            menu_schema.submenus = submenus_schemas
            menu_schema.get_counts()
            return menu_schema

@main_router.delete('/menus/{target_menu_id}', response_model=schemas.MenuIdOnly)
async def menu_delete(target_menu_id: UUID, db: AsyncSession = Depends(get_db)):
    delete_menu = await _menu_delete(target_id=target_menu_id, db=db)
    return delete_menu

async def _menu_delete(target_id: UUID, db: AsyncSession):
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            deletion = await menu_dal.delete_menu(target_id)
            if deletion is True:
                return schemas.MenuIdOnly(menu_id=target_id)
            raise HTTPException(status_code=404, detail='Menu not found')

@main_router.patch('/menus/{target_menu_id}', response_model=schemas.MenuRead)
async def menu_patch(target_menu_id: UUID, update_menu: schemas.MenuCreate, db: AsyncSession = Depends(get_db)):
    update_menu = await _menu_patch(target_menu_id=target_menu_id, updated_menu=update_menu, db=db)
    return update_menu

async def _menu_patch(target_menu_id: str, updated_menu: schemas.MenuCreate, db: AsyncSession):
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            updated_menu = await menu_dal.update_menu(menu_id=target_menu_id, updated_menu=updated_menu)
            if updated_menu is None:
                raise HTTPException(status_code=404, detail='Menu not found')
            return schemas.MenuRead(**updated_menu.__dict__)

@main_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
                 response_model=List[schemas.DishRead])
async def list_dishes(target_menu_id: str, target_submenu_id: str,
                      db: AsyncSession = Depends(get_db)) -> List[schemas.DishRead]:
    dishes = await _list_dishes(target_submenu_id=target_submenu_id, db=db)
    return dishes


async def _list_dishes(target_submenu_id: str, db: AsyncSession) -> List[schemas.DishRead]:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            dishes = await menu_dal.dishes_list(target_submenu_id=target_submenu_id)
            return [schemas.DishRead(**dish.__dict__) for dish in dishes]


@main_router.post('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes', status_code=201, response_model=schemas.DishRead)
async def dish_create(target_menu_id: str, target_submenu_id: str, dish: schemas.DishCreate,
                      db: AsyncSession = Depends(get_db)) -> schemas.DishRead:
    new_dish = await _dish_create(schemas.DishCreateWithSubmenuId(submenu_id=target_submenu_id,
                                                                  **dish.model_dump()), db)
    return new_dish


async def _dish_create(dish: schemas.DishCreateWithSubmenuId, db: AsyncSession) -> schemas.DishRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            new_dish = await menu_dal.create_dish(dish=dish)
            return DishRead(**new_dish.__dict__).round_price()


@main_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}',
                 status_code=200, response_model=schemas.DishRead)
async def dish_read(target_menu_id: str, target_submenu_id: str, target_dish_id: str,
                    db: AsyncSession = Depends(get_db)) -> schemas.DishRead:
    dish = await _dish_read(target_dish_id=target_dish_id, db=db)
    return dish


async def _dish_read(target_dish_id: str, db: AsyncSession) -> schemas.DishRead:
    async with db as db_session:
        async with db_session.begin():
            print('************\n\n\nTARGET DISH ID IS ***** \n\n\\n\n', target_dish_id)
            menu_dal = MenuDAL(db_session=db_session)
            dish = await menu_dal.read_object(object_id=target_dish_id, object_name='dish', object_class=Dish)
            return schemas.DishRead(**dish.__dict__).round_price()

@main_router.patch('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}',
                 status_code=200, response_model=schemas.DishRead)
async def dish_patch(target_menu_id: str, target_submenu_id: str, target_dish_id: str, dish_update: schemas.DishCreate,
                    db: AsyncSession = Depends(get_db)) -> schemas.DishRead:
    dish = await _dish_patch(target_dish_id=target_dish_id, dish_update=dish_update, db=db)
    return dish

async def _dish_patch(target_dish_id: str, dish_update: schemas.DishCreate, db: AsyncSession) -> schemas.DishRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            dish_patch = await menu_dal.dish_patch(target_dish_id=target_dish_id, update_dish=dish_update)
            return schemas.DishRead(**dish_patch.__dict__).round_price()


@main_router.delete('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes'
                        '/{target_dish_id}', response_model=schemas.DishIdOnly)
async def dish_delete(target_dish_id: str, db: AsyncSession = Depends(get_db)) -> schemas.DishIdOnly:
    delete_dish = await _dish_delete(target_dish_id=target_dish_id, db=db)
    return delete_dish

async def _dish_delete(target_dish_id: str, db: AsyncSession) -> schemas.DishIdOnly:
    async with db as db_session:
        async with db.begin():
            menu_dal = MenuDAL(db_session=db_session)
            dish_object = await menu_dal.read_object(object_name='dish', object_id=target_dish_id, object_class=Dish)
            deletion = await menu_dal.delete_object(dish_object)
            delete = deletion
            return schemas.DishIdOnly(id=target_dish_id)


##TODO Сделать проверку на существования отдельным методов в классе ДАЛ и потом уже везде его вызывать

































@main_router.get('/menus/{target_menu_id}/submenus', response_model=List[schemas.SubmenuRead])
async def submenus_read(target_menu_id: str, db: AsyncSession = Depends(get_db)) -> List[schemas.SubmenuRead]:
    submenu_list = await _submenus_read(target_menu_id=target_menu_id, db=db)
    return submenu_list

async def _submenus_read(target_menu_id: str, db: AsyncSession) -> List[schemas.SubmenuRead]:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            menu = await menu_dal.read_object(object_name='menu', object_id=target_menu_id, object_class=Menu)
            return [schemas.SubmenuRead(**submenu.__dict__).get_dishes_count() for submenu in menu.submenus]

@main_router.post('/menus/{target_menu_id}/submenus', status_code=201, response_model=schemas.SubmenuRead)
async def submenu_create(target_menu_id: str, submenu: schemas.SubmenuCreate, db: AsyncSession = Depends(get_db)):
    create_submenu = schemas.SubmenuCreateWithMenuId(menu_id=target_menu_id, **submenu.model_dump())
    new_submenu = await _submenu_create(submenu=create_submenu, db=db)
    return new_submenu

async def _submenu_create(submenu: schemas.SubmenuCreate, db: AsyncSession) -> schemas.SubmenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db_session)
            new_submenu = await menu_DAL.create_submenu(submenu)
            return SubmenuRead(**new_submenu.__dict__)


@main_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}', response_model=schemas.SubmenuRead)
async def submenu_read(target_menu_id: str, target_submenu_id: str, db: AsyncSession = Depends(get_db)) -> schemas.SubmenuRead:
    target_submenu = await _submenu_read(target_submenu_id, db=db)
    return target_submenu.get_dishes_count()


## IMPORTANT BLYAT!
async def _submenu_read(target_submenu_id: str, db: AsyncSession) -> schemas.SubmenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db_session)
            target_submenu = await menu_DAL.submenu_read(submenu_id=target_submenu_id)
            submenu_schema = schemas.SubmenuRead(**target_submenu.__dict__)
            submenu_schema.dishes = [schemas.DishRead(**dish.__dict__) for dish in target_submenu.dishes]
            return submenu_schema


@main_router.delete('/menus/{target_menu_id}/submenus/{target_submenu_id}', response_model=schemas.SubmenuIdOnly)
async def submenu_delete(target_menu_id: str, target_submenu_id: str, db: AsyncSession = Depends(get_db)):
    delete_submenu = await _submenu_delete(target_submenu_id, db=db)
    return delete_submenu

async def _submenu_delete(target_submenu_id: str, db: AsyncSession) -> schemas.SubmenuIdOnly:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db)
            deletion = await menu_DAL.submenu_delete(submenu_id=target_submenu_id)
            return schemas.SubmenuIdOnly(submenu_id=target_submenu_id)

@main_router.patch('/menus/{target_menu_id}/submenus/{target_submenu_id}', response_model=schemas.SubmenuRead)
async def submenu_patch(target_menu_id: str, target_submenu_id: str,
                        update_menu: schemas.SubmenuCreate, db: AsyncSession = Depends(get_db)) -> schemas.SubmenuRead:
    update_menu = await _submenu_patch(target_submenu_id=target_submenu_id,
                                       updated_menu=update_menu, db=db)
    return update_menu


async def _submenu_patch(target_submenu_id: str, updated_menu: schemas.SubmenuCreate, db: AsyncSession):
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            update_menu = await menu_dal.submenu_update(target_submenu_id=target_submenu_id,
                                                        updated_submenu=updated_menu)
            if updated_menu is None:
                raise HTTPException(status_code=404, detail='Submenu not found')
            return schemas.SubmenuRead(**update_menu.__dict__)










