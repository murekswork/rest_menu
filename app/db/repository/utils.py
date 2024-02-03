from sqlalchemy import distinct, func, select

from app.db.models import Dish, Menu, SubMenu

from .crud import UUID, MenuCrud


class MenuUTIL(MenuCrud):

    async def read_menu_with_counts(self, menu_id: UUID):
        check_exist = await self.read_object(object_class=Menu, object_id=menu_id)
        if check_exist is None:
            return None
        query = (select(
            Menu.id,
            Menu.title,
            Menu.description,
            func.count(distinct(SubMenu.id)).label('submenu_count'),
            func.count(distinct(Dish.id)).label('dish_count')
        ).select_from(Menu)
            .outerjoin(SubMenu, SubMenu.menu_id == Menu.id)
            .outerjoin(Dish, Dish.submenu_id == SubMenu.id)
            .where(Menu.id == menu_id)
            .group_by(Menu.id))
        result = (await self.db_session.execute(query)).fetchone()
        return result
