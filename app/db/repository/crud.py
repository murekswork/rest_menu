from typing import Any
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import Dish, Menu, SubMenu


class Repository:

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session


class MenuCrud(Repository):
    """
        # Description
        The MenuCrud class provides CRUD (Create, Read, Update, Delete) methods for
        interacting with a database, including creating, reading, updating, and deleting objects of VARIOUS classes.

        # Methods
        The DAL class contains the following methods:
        1. create_object: Used to create a new object in the database.
        2. get_object: Used to retrieve an object from the database based on its ID.
        3. update_object: Used to update an existing object in the database.
        4. delete_object: Used to delete an object from the database based on its ID.

        ## Dependencies
        Objects of this class require an active database session to be initialized.

        # Error Handling
        The CRUD class methods may raise HTTPExceptions with appropriate status codes if errors occur during database
        operations, such as object not found or database connection issues.

        # Additional Notes
        - The CRUD class provides a convenient interface for performing common database operations and can be extended
        to include additional functionality as needed. It encapsulates the logic for interacting with the database,
        making it easier to manage database operations within the application.
    """

    async def create_object(self,
                            object_class: type[Menu | SubMenu | Dish],
                            object_schema: BaseModel,
                            parent_class: type[Menu | SubMenu | Dish] | None = None,
                            parent_id: UUID | None = None):
        """

        The create_object function is used to create a new object based on a given object schema and class.
        It also supports associating the new object with a parent object.

        :param object_class: The class of the object to be created
        :param object_schema: The schema of the object containing its data
        :param parent_class: (Optional) The Class of the parent object. Required when created object has parent.
        :param parent_id: (Optional) The ID of the parent object. Required when created object has parent.
        :return: The function returns the newly created object.

        :Error Handling
        - The function may raise an HTTPException with a status code of 404 if the parent object is not found
        """
        if parent_class and parent_id:
            check_parent_exist_query = select(parent_class).where(parent_class.id == parent_id)
            check_result = (await self.db_session.execute(check_parent_exist_query)).scalar()
            if check_result is None:
                raise HTTPException(status_code=404, detail=f'{parent_class.__name__} not found')
        new_object = object_class(**object_schema.model_dump())
        self.db_session.add(new_object)
        await self.db_session.flush()
        return new_object

    async def read_object(self,
                          object_name: str,
                          object_id: UUID,
                          object_class: type[Menu | SubMenu | Dish]) -> Any:
        """
        The read_object function is used to retrieve an object from the database based on its name, ID, and class.
        It supports loading related objects based on the class type.

        :param object_name: A string representing the name of the object.
        :param object_id: A UUID representing the ID of the object to be retrieved.
        :param object_class: The class of the object to be retrieved.
        :return: The function returns found object.

        :Error Handling
        - The function may raise an HTTPException with a status code of 404 if the object is not found in the database.
        """
        query = select(object_class).where(object_class.id == object_id)

        if object_class is Menu:
            query = query.options(joinedload(object_class.submenus).joinedload(SubMenu.dishes))

        elif object_class is SubMenu:
            query = query.options(joinedload(SubMenu.dishes))

        elif object_class is Dish:
            query = query

        obj = (await self.db_session.execute(query)).scalar()

        if obj is None:
            raise HTTPException(status_code=404, detail=f'{object_name} not found')
        return obj

    async def read_objects(self,
                           object_name: str,
                           object_class: type[Menu | SubMenu | Dish],
                           **ids) -> Any:
        """
        The read_objects function is used to retrieve objects from the database based on their
        name, class, and additional IDs. It supports loading related objects based on the class type,
        such as submenus and dishes for menus.

        :param object_name: A string representing the name of the object.
        :param object_class: The class of the object to be retrieved.
        :param ids: Additional keyword arguments representing the IDs required for retrieving related objects.
        :return: The function returns the retrieved objects from the database.

        :Error Handling
        - The function may raise an HTTPException with a status code of 404 if the objects are not found in the database
        """
        if object_class is Menu:
            query = select(object_class).options(joinedload(object_class.submenus).joinedload(SubMenu.dishes))

        if object_class is Dish:
            query = select(object_class).where(object_class.submenu_id == ids['submenu_id'])

        objects = (await self.db_session.execute(query))

        if objects is None:
            raise HTTPException(status_code=404, detail=f'{object_name}s not found')

        return objects.scalars().unique()

    async def update_object(self,
                            object_id: UUID,
                            object_class: type[Menu | SubMenu | Dish],
                            object_schema: BaseModel) -> Any:
        """
        The update_object function is used to update an object in the database based on its ID, class, and schema.

        :param object_id: A UUID representing the ID of the object to be retrieved.
        :param object_class: The class of the object to be updated.
        :param object_schema: An instance of the schema class containing the updated data for the object.
        :return: The function returns the updated object from the database.

        :Error Handling
        - The function may raise an HTTPException with a status code of 404 if the object with the specified ID
        is not found in the database.
        """
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

    async def delete_object(self,
                            object_class: type[Menu | SubMenu | Dish],
                            object_id: UUID) -> bool:
        """
        The delete_object function is used to delete an object from the database based on its ID and class.

        :param object_class: The class of the object to be deleted.
        :param object_id: A UUID representing the ID of the object to be deleted.
        :return: The function returns a boolean value indicating the success of the deletion operation.

        :Error Handling
        - The function may raise an HTTPException with a status code of 404 if the object with the specified
        ID is not found in the database.
        """
        check_exist_query = select(object_class).where(object_class.id == object_id)
        check_result = (await self.db_session.execute(check_exist_query)).scalar()
        if check_result is None:
            raise HTTPException(status_code=404, detail=f'{object_class.__name__} not found')
        query = delete(object_class).where(object_class.id == object_id)
        await self.db_session.execute(query)
        await self.db_session.flush()
        return True
