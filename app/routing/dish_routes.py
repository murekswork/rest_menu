from ..routers import *

dish_router = APIRouter()


@dish_router.patch('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}',
                   status_code=200,
                   response_model=schemas.DishRead)
async def dish_patch(target_menu_id: UUID,
                     target_submenu_id: UUID,
                     target_dish_id: UUID,
                     dish_update: schemas.DishCreate,
                     db: AsyncSession = Depends(get_db)) -> schemas.DishRead:
    dish = await _dish_patch(target_dish_id=target_dish_id,
                             dish_update=dish_update,
                             db=db)
    return dish


async def _dish_patch(target_dish_id: UUID,
                      dish_update: schemas.DishCreate,
                      db: AsyncSession) -> schemas.DishRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            update_result = await menu_dal.update_object(object_class=Dish,
                                                         object_id=target_dish_id,
                                                         object_schema=dish_update)
            return schemas.DishRead(**update_result.__dict__).round_price()


@dish_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
                 response_model=List[schemas.DishRead])
async def list_dishes(target_menu_id: UUID,
                      target_submenu_id: UUID,
                      db: AsyncSession = Depends(get_db)) -> List[schemas.DishRead]:
    dishes = await _list_dishes(target_submenu_id=target_submenu_id, db=db)
    return dishes


async def _list_dishes(target_submenu_id: UUID,
                       db: AsyncSession) -> List[schemas.DishRead]:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            dishes = await menu_dal.read_objects(submenu_id=target_submenu_id,
                                                 object_class=Dish,
                                                 object_name='dish')
            return [schemas.DishRead(**dish.__dict__) for dish in dishes]


@dish_router.post('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
                  status_code=201,
                  response_model=schemas.DishRead)
async def dish_create(target_menu_id: UUID,
                      target_submenu_id: UUID,
                      dish_schema: schemas.DishCreate,
                      db: AsyncSession = Depends(get_db)) -> schemas.DishRead:
    dish_schema = schemas.DishCreateWithSubmenuId(**dish_schema.model_dump(),
                                                  submenu_id=target_submenu_id)
    new_dish = await _dish_create(dish_schema, db)
    return new_dish


async def _dish_create(dish_schema: schemas.DishCreateWithSubmenuId,
                       db: AsyncSession) -> schemas.DishRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            new_dish = await menu_dal.create_object(object_schema=dish_schema,
                                                    object_class=Dish,
                                                    parent_id=dish_schema.submenu_id,
                                                    parent_class=SubMenu)
            return DishRead(**new_dish.__dict__).round_price()


@dish_router.get('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}',
                 status_code=200,
                 response_model=schemas.DishRead)
async def dish_read(target_menu_id: UUID,
                    target_submenu_id: UUID,
                    target_dish_id: UUID,
                    db: AsyncSession = Depends(get_db)) -> schemas.DishRead:
    dish = await _dish_read(target_dish_id=target_dish_id, db=db)
    return dish


async def _dish_read(target_dish_id: UUID, db: AsyncSession) -> schemas.DishRead:
    async with db as db_session:
        async with db_session.begin():
            menu_dal = MenuDAL(db_session=db_session)
            object_db = await menu_dal.read_object(object_id=target_dish_id, object_name='dish', object_class=Dish)
            return schemas.DishRead(**object_db.__dict__).round_price()


@dish_router.delete('/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes'
                    '/{target_dish_id}', response_model=schemas.DishIdOnly)
async def dish_delete(target_dish_id: UUID, db: AsyncSession = Depends(get_db)) -> schemas.DishIdOnly:
    delete_dish = await _dish_delete(target_dish_id=target_dish_id, db=db)
    return delete_dish


async def _dish_delete(target_dish_id: UUID, db: AsyncSession) -> schemas.DishIdOnly:
    async with db as db_session:
        async with db.begin():
            menu_dal = MenuDAL(db_session=db_session)
            deletion = await menu_dal.delete_object(object_class=Dish,
                                                    object_id=target_dish_id)
            return schemas.DishIdOnly(id=target_dish_id)
