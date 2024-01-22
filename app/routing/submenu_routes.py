from ..routers import *

submenu_router = APIRouter()


@submenu_router.get('/menus/{target_menu_id}/submenus', response_model=List[schemas.SubmenuRead])
async def submenus_read(target_menu_id: UUID,
                        db: AsyncSession = Depends(get_db)) -> List[schemas.SubmenuRead]:
    submenu_list = await _submenus_read(target_menu_id=target_menu_id, db=db)
    return submenu_list


async def _submenus_read(target_menu_id: UUID, db: AsyncSession) -> List[schemas.SubmenuRead]:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            menu_db = await menu_dal.read_object(object_name='menu',
                                                 object_id=target_menu_id,
                                                 object_class=Menu)
            submenus_schemas = []
            for submenu in menu_db.submenus:
                submenu_schema = schemas.SubmenuRead(**submenu.__dict__)
                dish_schemas = [schemas.DishRead(**dish.__dict__).round_price() for dish in submenu.dishes]
                submenu_schema.dishes = dish_schemas
                submenu_schema.get_dishes_count()
                submenus_schemas.append(submenu_schema)

            return submenus_schemas


@submenu_router.post('/menus/{target_menu_id}/submenus',
                     status_code=201,
                     response_model=schemas.SubmenuRead)
async def submenu_create(target_menu_id: str, submenu_schema: schemas.SubmenuCreate,
                         db: AsyncSession = Depends(get_db)):
    submenu_schema_with_menu_id = schemas.SubmenuCreateWithMenuId(menu_id=target_menu_id, **submenu_schema.model_dump())
    new_submenu = await _submenu_create(submenu_schema=submenu_schema_with_menu_id, db=db)
    return new_submenu


async def _submenu_create(submenu_schema: schemas.SubmenuCreateWithMenuId, db: AsyncSession) -> schemas.SubmenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db_session)
            new_submenu = await menu_DAL.create_object(object_class=SubMenu,
                                                       object_schema=submenu_schema,
                                                       parent_id=submenu_schema.menu_id,
                                                       parent_class=Menu)
            return SubmenuRead(**new_submenu.__dict__)


@submenu_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}', response_model=schemas.SubmenuRead)
async def submenu_read(target_menu_id: str, target_submenu_id: str,
                       db: AsyncSession = Depends(get_db)) -> schemas.SubmenuRead:
    target_submenu = await _submenu_read(target_submenu_id, db=db)
    return target_submenu.get_dishes_count()


async def _submenu_read(target_submenu_id: str, db: AsyncSession) -> schemas.SubmenuRead:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db_session)
            target_submenu = await menu_DAL.read_object(object_id=target_submenu_id, object_name='submenu',
                                                        object_class=SubMenu)
            submenu_schema = schemas.SubmenuRead(**target_submenu.__dict__)
            submenu_schema.dishes = [schemas.DishRead(**dish.__dict__) for dish in target_submenu.dishes]
            return submenu_schema


@submenu_router.delete('/menus/{target_menu_id}/submenus/{target_submenu_id}', response_model=schemas.SubmenuIdOnly)
async def submenu_delete(target_menu_id: UUID, target_submenu_id: UUID, db: AsyncSession = Depends(get_db)):
    delete_submenu = await _submenu_delete(target_submenu_id, db=db)
    return delete_submenu


async def _submenu_delete(target_submenu_id: UUID, db: AsyncSession) -> schemas.SubmenuIdOnly:
    async with db as db_session:
        async with db_session.begin():
            menu_DAL = MenuDAL(db_session=db)
            deletion = await menu_DAL.delete_object(object_id=target_submenu_id, object_class=SubMenu)
            return schemas.SubmenuIdOnly(submenu_id=target_submenu_id)


@submenu_router.patch('/menus/{target_menu_id}/submenus/{target_submenu_id}',
                      status_code=200, response_model=schemas.SubmenuRead)
async def submenu_patch(target_menu_id: UUID, target_submenu_id: UUID,
                        submenu_update: schemas.SubmenuCreate,
                        db: AsyncSession = Depends(get_db)) -> schemas.SubmenuRead:
    submenu = await _submenu_patch(target_submenu_id=target_submenu_id,
                                   submenu_update=submenu_update, db=db)
    return submenu


async def _submenu_patch(target_submenu_id: UUID, submenu_update: schemas.SubmenuCreate, db: AsyncSession):
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            update_result = await menu_dal.update_object(object_class=SubMenu,
                                                         object_id=target_submenu_id,
                                                         object_schema=submenu_update)
            return schemas.SubmenuRead(**update_result.__dict__)
