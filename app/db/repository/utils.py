from uuid import UUID

from sqlalchemy import select

from app.db.models import Dish, Menu, SubMenu
from app.db.repository.crud import MenuCrud


class AdvancedMenuRepository(MenuCrud):

    async def read_by_kwargs(self,
                             obj_class: type[Menu | SubMenu | Dish],
                             title: str,
                             description: str) -> UUID | None:
        """Read objects by title and description"""
        query = select(obj_class).where(
            obj_class.title == title,
            obj_class.description == description
        )
        obj = (await self.db_session.execute(query)).scalar()
        await self.db_session.commit()
        if obj:
            return obj.id
        return None

    async def get_all_ids(self, object_class: type[Menu | SubMenu | Dish]):
        """Read all objects of passed class and return ids"""
        query = select(object_class.id)
        ids = await self.db_session.execute(query)
        return [str(i) for (i,) in ids]
