from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.schemas import SubmenuRead, DishRead
from db.session import get_db
from app import schemas
from db.crud import MenuDAL

main_router = APIRouter()


@main_router.post('/menus/create', response_model=schemas.MenuRead)
async def menu_create(menu: schemas.MenuCreate, db: AsyncSession = Depends(get_db)):
    new_menu = await _menu_create(menu, db)
    return new_menu
async def _menu_create(menu: schemas.MenuCreate, db: AsyncSession) -> schemas.MenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            new_menu = await menu_dal.create_menu(menu)
            return schemas.MenuRead(**new_menu.__dict__)


@main_router.get('/menus/{target_menu_id}/', response_model=schemas.MenuRead)
async def menu_read(target_menu_id: int, db: AsyncSession = Depends(get_db)):
    menu = await _menu_read(target_id=target_menu_id, db=db)
    return menu

async def _menu_read(target_id: int, db: AsyncSession) -> schemas.MenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            menu = await menu_dal.read_menu(menu_id=target_id)
            return schemas.MenuRead(**menu.__dict__)

@main_router.delete('/menus/{target_menu_id}/', response_model=schemas.MenuIdOnly)
async def menu_delete(target_menu_id: int, db: AsyncSession = Depends(get_db)):
    delete_menu = await _menu_delete(target_id=target_menu_id, db=db)
    return delete_menu

async def _menu_delete(target_id: int, db: AsyncSession):
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            deletion = menu_dal.delete_menu(target_id)
            return schemas.MenuIdOnly(menu_id=target_id)





@main_router.post('/menu/submenu/dish/create', response_model=schemas.DishRead)
async def dish_create(dish: schemas.DishCreate, db: AsyncSession = Depends(get_db)):
    new_dish = await _dish_create(db=db, dish=dish)
    return dish

async def _dish_create(dish: schemas.DishCreate, db: AsyncSession) -> schemas.DishRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            new_dish = await menu_dal.create_dish(dish=dish)
            return DishRead(**new_dish.__dict__)






































@main_router.post('/menu/{target_menu_id}/submenus/create', response_model=schemas.SubmenuRead)
async def submenu_create(submenu: schemas.SubmenuCreate, db: AsyncSession = Depends(get_db)):
    new_submenu = await _submenu_create(submenu=submenu, db=db)
    return new_submenu

async def _submenu_create(submenu: schemas.SubmenuCreate, db: AsyncSession) -> schemas.SubmenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db_session)
            new_submenu = await menu_DAL.create_submenu(submenu)
            return SubmenuRead(**new_submenu.__dict__)


@main_router.get('/menu/{target_menu_id}/{target_submenu_id}', response_model=schemas.SubmenuRead)
async def submenu_read(target_menu_id: int, target_submenu_id: int, db: AsyncSession = Depends(get_db)) -> schemas.SubmenuRead:
    target_submenu = await _submenu_read(target_submenu_id, db=db)
    return target_submenu

async def _submenu_read(target_submenu_id: int, db: AsyncSession) -> schemas.SubmenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db_session)
            target_submenu = await menu_DAL.submenu_read(target_submenu_id)
            return schemas.SubmenuRead(**target_submenu.__dict__)


@main_router.delete('/menu/{target_menu_id}/{target_submenu_id}', response_model=schemas.SubmenuIdOnly)
async def submenu_delete(target_menu_id: int, target_submenu_id: int, db: AsyncSession = Depends(get_db)):
    delete_submenu = await _submenu_delete(target_submenu_id, db=db)
    return delete_submenu

async def _submenu_delete(target_submenu_id: int, db: AsyncSession) -> schemas.SubmenuIdOnly:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db)
            deletion = await menu_DAL.submenu_delete(submenu_id=target_submenu_id)
            return schemas.SubmenuIdOnly(submenu_id=target_submenu_id)
















