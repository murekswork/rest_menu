from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app import schemas
from .models import *


class MenuDAL:

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_object(self, object_class, object_schema: schemas, parent_class=None, parent_id=None):
        if parent_class and parent_id:
            check_parent_exist_query = select(parent_class).where(parent_class.id == parent_id)
            check_result = (await self.db_session.execute(check_parent_exist_query)).scalar()
            if check_result is None:
                raise HTTPException(status_code=404, detail=f"{parent_class.__name__} not found")
        new_object = object_class(**object_schema.model_dump())
        self.db_session.add(new_object)
        await self.db_session.flush()
        return new_object

    async def read_object(self, object_name: str, object_id: UUID, object_class):
        query = select(object_class).where(object_class.id == object_id)

        if object_class is Menu:
            query = query.options(joinedload(object_class.submenus).joinedload(SubMenu.dishes))

        elif object_class is SubMenu:
            query = query.options(joinedload(SubMenu.dishes))

        elif object_class is Dish:
            query = query

        object = (await self.db_session.execute(query)).scalar()

        if object is None:
            raise HTTPException(status_code=404, detail=f'{object_name} not found')
        return object

    async def read_objects(self, object_name: str, object_class, **ids):
        if object_class is Menu:
            query = select(object_class).options(joinedload(object_class.submenus).joinedload(SubMenu.dishes))

        if object_class is Dish:
            query = select(object_class).where(object_class.submenu_id == ids['submenu_id'])

        objects = (await self.db_session.execute(query))

        if objects is None:
            raise HTTPException(status_code=404, detail=f'{object_name}s not found')

        return objects.scalars().unique()

    async def update_object(self, object_id: UUID, object_class, object_schema: schemas):
        check_exist_query = select(object_class).where(object_class.id == object_id)
        check_result = (await self.db_session.execute(check_exist_query)).scalar()
        if check_result is None:
            raise HTTPException(status_code=404, detail=f'{object_class.__name__} not found')
        query = update(object_class).where(object_class.id == object_id).values(**object_schema.model_dump())
        await self.db_session.execute(query)
        await self.db_session.flush()
        query = select(object_class).where(object_class.id == object_id)
        result = (await self.db_session.execute(query)).scalar()
        return result

    async def delete_object(self, object_class, object_id: UUID):
        check_exist_query = select(object_class).where(object_class.id == object_id)
        check_result = (await self.db_session.execute(check_exist_query)).scalar()
        if check_result is None:
            raise HTTPException(status_code=404, detail=f'{object_class.__name__} not found')
        query = delete(object_class).where(object_class.id == object_id)
        await self.db_session.execute(query)
        await self.db_session.flush()
        return True
