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

    async def read_menu(self, menu_id: int) -> Menu:
        query = select(Menu).where(Menu.menu_id == menu_id).options(joinedload(Menu.submenus).joinedload(SubMenu.dishes))
        res = await self.db_session.execute(query)
        menu = res.scalar()
        if menu:
            return menu
        else:
            raise HTTPException(status_code=403, detail="Menu not found")

    async def delete_menu(self, menu_id: int) -> HTTPException | True:
        try:
            qeury = delete(Menu).where(Menu.menu_id == menu_id)
            result = await self.db_session.execute(qeury)
            return True
        except:
            raise HTTPException(status_code=403, detail='Menu with this menu_id doesnt exist')

    async def create_submenu(self, submenu: schemas.SubmenuCreate) -> SubMenu:
        new_submenu = SubMenu(**submenu.model_dump())
        try:
            self.db_session.add(new_submenu)
            await self.db_session.flush()
        except Exception as e:
            raise HTTPException(status_code=403, detail='Menu with this menu_id doesnt exist')
        return new_submenu

    async def submenu_read(self, submenu_id: int) -> SubMenu:
        query = select(SubMenu).where(SubMenu.submenu_id == submenu_id).options(joinedload(SubMenu.dishes))
        rez = await self.db_session.execute(query)
        submenu = rez.scalar()
        if submenu:
            return submenu
        else:
            raise HTTPException(status_code=403, detail='Submenu with this submenu_id doesnt exist')

    async def submenu_delete(self, submenu_id: int) -> HTTPException | True:
        try:
            query = delete(SubMenu).where(SubMenu.submenu_id == submenu_id)
            result = await self.db_session.execute(query)
            return True
        except Exception as e:
            raise HTTPException(status_code=403, detail='Submenu with this submenu_id doesnt exist')

    async def create_dish(self, dish: schemas.DishCreate) -> Dish:
        new_dish = Dish(**dish.model_dump())
        try:
            self.db_session.add(new_dish)
            await self.db_session.flush()
        except Exception as e:
            raise HTTPException(status_code=403, detail='Submenu with this id doesnt exist')
        return new_dish