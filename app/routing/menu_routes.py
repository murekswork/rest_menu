from ..routers import *

menu_router = APIRouter()


@menu_router.get("/menus", response_model=List[schemas.MenuRead])
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


@menu_router.post('/menus', status_code=201, response_model=schemas.MenuRead)
async def menu_create(menu_schema: schemas.MenuCreate, db: AsyncSession = Depends(get_db)):
    new_menu = await _menu_create(menu_schema, db)
    return new_menu


async def _menu_create(menu_schema: schemas.MenuCreate, db: AsyncSession) -> schemas.MenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            new_menu = await menu_dal.create_object(object_class=Menu, object_schema=menu_schema)
            return schemas.MenuRead(**new_menu.__dict__)


@menu_router.get('/menus/{target_menu_id}', response_model=schemas.MenuRead)
async def menu_read(target_menu_id: UUID, db: AsyncSession = Depends(get_db)):
    menu = await _menu_read(target_menu_id=target_menu_id, db=db)
    return menu


async def _menu_read(target_menu_id: UUID, db: AsyncSession) -> schemas.MenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            object_db = await menu_dal.read_object(object_id=target_menu_id, object_name='menu', object_class=Menu)
            menu_schema = schemas.MenuRead(**object_db.__dict__)
            submenus_schemas = []
            for submenu in object_db.submenus:
                submenu_schema = schemas.SubmenuRead(**submenu.__dict__)
                dish_schemas = [schemas.DishRead(**dish.__dict__).round_price() for dish in submenu.dishes]
                submenu_schema.dishes = dish_schemas
                submenu_schema.get_dishes_count()
                submenus_schemas.append(submenu_schema)

            menu_schema.submenus = submenus_schemas
            menu_schema.get_counts()
            return menu_schema


@menu_router.delete('/menus/{target_menu_id}', response_model=schemas.MenuIdOnly)
async def menu_delete(target_menu_id: UUID, db: AsyncSession = Depends(get_db)):
    delete_menu = await _menu_delete(target_id=target_menu_id, db=db)
    return delete_menu


async def _menu_delete(target_id: UUID, db: AsyncSession):
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            deletion = await menu_dal.delete_object(object_class=Menu, object_id=target_id)
            return schemas.MenuIdOnly(menu_id=target_id)


@menu_router.patch('/menus/{target_menu_id}', status_code=200, response_model=schemas.MenuRead)
async def menu_patch(target_menu_id: UUID, menu_update: schemas.MenuCreate, db: AsyncSession = Depends(get_db)):
    update_menu = await _menu_patch(target_menu_id=target_menu_id, menu_update=menu_update, db=db)
    return update_menu


async def _menu_patch(target_menu_id: UUID, menu_update: schemas.MenuCreate, db: AsyncSession) -> schemas.MenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            update_result = await menu_dal.update_object(object_class=Menu,
                                                         object_id=target_menu_id,
                                                         object_schema=menu_update)
            return schemas.MenuRead(**update_result.__dict__)


@menu_router.delete('/menus/{target_menu_id}', response_model=schemas.MenuIdOnly)
async def menu_delete(target_menu_id: UUID, db: AsyncSession = Depends(get_db)):
    delete_menu = await _menu_delete(target_id=target_menu_id, db=db)
    return delete_menu


async def _menu_delete(target_id: UUID, db: AsyncSession):
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            deletion = await menu_dal.delete_object(object_class=Menu, object_id=target_id)
            return schemas.MenuIdOnly(menu_id=target_id)
