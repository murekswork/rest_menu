import logging

from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .models import *
from app import schemas

class MenuDAL:

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_menu(self, menu: schemas.MenuCreate) -> Menu:
        new_menu = Menu(**menu.model_dump())
        self.db_session.add(new_menu)
        await self.db_session.flush()
        return new_menu

    async def read_menu(self, menu_id: str) -> Menu:
        query = select(Menu).where(Menu.id == menu_id).options(joinedload(Menu.submenus).joinedload(SubMenu.dishes))
        res = await self.db_session.execute(query)
        menu = res.scalar()
        if menu:
            return menu
        else:
            raise HTTPException(status_code=404, detail="Menu not found")

    async def read_all_menus(self) -> List[Menu]:
        query = select(Menu).options(joinedload(Menu.submenus).joinedload(SubMenu.dishes))
        res = await self.db_session.execute(query)
        return res.scalars().unique()

    async def delete_menu(self, menu_id: str):
            check_existance = select(Menu).where(Menu.id == menu_id)
            check_result = (await self.db_session.execute(check_existance)).scalar()
            if check_result is None:
                return False

            qeury = delete(Menu).where(Menu.id == menu_id)
            result = await self.db_session.execute(qeury)
            await self.db_session.commit()
            return True


    async def update_menu(self, menu_id: str, updated_menu: schemas.MenuCreate):
        query = update(Menu).where(Menu.id == menu_id).values(**updated_menu.model_dump())
        await self.db_session.execute(query)
        await self.db_session.flush()
        query = select(Menu).where(Menu.id == menu_id)
        result = await self.db_session.execute(query)
        return result.scalar()


    async def create_submenu(self, submenu: schemas.SubmenuCreate) -> SubMenu:
        new_submenu = SubMenu(**submenu.model_dump())
        try:
            self.db_session.add(new_submenu)
            await self.db_session.flush()
        except Exception as e:
            raise HTTPException(status_code=404, detail='Menu with this menu_id doesnt exist')
        return new_submenu

    async def submenu_read(self, submenu_id: int) -> SubMenu:
        query = select(SubMenu).where(SubMenu.id == submenu_id).options(joinedload(SubMenu.dishes))
        rez = await self.db_session.execute(query)
        submenu = rez.scalar()
        if submenu:
            return submenu
        else:
            raise HTTPException(status_code=404, detail='submenu not found')

    async def submenu_delete(self, submenu_id: str) -> Boolean:
        try:
            query = delete(SubMenu).where(SubMenu.id == submenu_id)
            result = await self.db_session.execute(query)
            return True
        except Exception as e:
            raise HTTPException(status_code=4, detail=f'{e}')

    async def submenus_read(self, target_menu_id: str) -> List[SubMenu]:
        query = select(SubMenu).where(SubMenu.menu_id == target_menu_id)
        result = (await self.db_session.execute(query)).scalars()
        return result

    async def submenu_update(self, target_submenu_id: str, updated_submenu: schemas.SubmenuCreate) -> SubMenu:
        query = update(SubMenu).where(SubMenu.id == target_submenu_id).values(**updated_submenu.model_dump())
        await self.db_session.execute(query)
        await self.db_session.flush()
        query = select(SubMenu).where(SubMenu.id == target_submenu_id)
        result = await self.db_session.execute(query)
        return result.scalar()

    async def create_dish(self, dish: schemas.DishCreateWithSubmenuId) -> Dish:
        check_submenu_existance = select(SubMenu).where(SubMenu.id == dish.submenu_id)
        check_result = (await self.db_session.execute(check_submenu_existance)).scalar()
        if check_result is None:
            raise HTTPException(status_code=404, detail='submenu not found')
        new_dish = Dish(**dish.model_dump())
        self.db_session.add(new_dish)
        await self.db_session.flush()
        return new_dish


    async def dishes_list(self, target_submenu_id: str) -> List[Dish]:
        query = select(Dish).where(Dish.submenu_id == target_submenu_id)
        dishes = (await self.db_session.execute(query)).scalars()
        return dishes

    async def read_object(self, object_name: str, object_id: str, object_class):
        query = select(object_class).where(object_class.id == object_id)

        if object_class is Menu:
            query = query.options(joinedload(object_class.submenus).joinedload(SubMenu.dishes))

        elif object_class is SubMenu:
            query = query.options(joinedload(SubMenu.dishes))

        object = (await self.db_session.execute(query)).scalar()

        if object is None:
            raise HTTPException(status_code=404, detail=f'{object_name} not found')
        return object
    
    async def read_objects(self, object_name: str, object_class):
        query = select(object_class).options(joinedload(object_class.submenus).joinedload(SubMenu.dishes))
        objects = (await self.db_session.execute(query)).scalars().unique()
        return objects



    async def dish_read(self, target_dish_id) -> Dish:
        query = select(Dish).where(Dish.id == target_dish_id)
        rez = await self.db_session.execute(query)
        dish = rez.scalar()
        if dish:
            return dish
        else:
            raise HTTPException(status_code=404, detail='dish not found')

    async def dish_patch(self, target_dish_id: str, update_dish: schemas.DishCreate):
        query = update(Dish).where(Dish.id == target_dish_id).values(**update_dish.model_dump())
        await self.db_session.execute(query)
        await self.db_session.flush()
        query = select(Dish).where(Dish.id == target_dish_id)
        result = await self.db_session.execute(query)
        return result.scalar()

    async def dish_delete(self, target_dish_id: str):
        dish_db = select(Dish).where(Dish.id == target_dish_id)
        dish_db = await self.db_session.execute(dish_db)
        dish_db = dish_db.scalar()
        deletion = await self.db_session.delete(dish_db)
        await self.db_session.commit()
        print('TYPE OF DISH ID IS: ', type(dish_db))
        return True

    async def delete_object(self, object):
        deletion = await self.db_session.delete(object)
        logging.warning(f'******* Object ******* {object}')
        await self.db_session.commit()
        return True

    # async def delete_object(self, object):
    #     object_class = object.__class__
    #     print(object_class.__name__, object, object_class, '******************!!!!!!!!!!!!!!**************')
    #     check_existance = select(object_class).where(object_class.id == object.id)
    #     result = await self.db_session.execute(check_existance)
    #     print(result.scalar())

