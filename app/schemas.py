from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class TunedModel(BaseModel):

    class Config:
        from_attributes = True
        orm_mode = True


class DishRead(TunedModel):
    id: UUID
    title: str
    price: float | str
    description: str

    def round_price(self):
        self.price = ("%.2f" % self.price)
        return self

class DishCreate(BaseModel):
    title: str
    price: float
    description: str

class DishCreateWithSubmenuId(DishCreate):
    submenu_id: UUID

class DishIdOnly(BaseModel):
    id: UUID


class MenuCreate(BaseModel):
    title: str
    description: str



class MenuCreateRead(MenuCreate):
    menu_id: UUID

class MenuIdOnly(BaseModel):
    menu_id: UUID



class SubmenuCreate(BaseModel):

    title: str
    description: str = 'description'

class SubmenuCreateWithMenuId(SubmenuCreate):
    menu_id: UUID


class SubmenuRead(TunedModel):
    id: UUID
    title: str
    description: str = 'description'
    dishes_count: int = 0
    dishes: List[DishRead] | List = []

    def get_dishes_count(self):
        self.dishes_count = len(self.dishes)
        return self

class SubmenuIdOnly(BaseModel):
    submenu_id: UUID

class MenuRead(TunedModel):
    id: UUID
    description: str
    title: str
    dishes_count: int | None = 0
    submenus_count: int | None = 0
    submenus: List[SubmenuRead] | List = None

    def get_counts(self):
        self.submenus_count = len(self.submenus)
        self.dishes_count = sum(submenu.dishes_count for submenu in self.submenus)
        return self

class MenuListSchema(BaseModel):

    menus: List[MenuRead]

class MenuReadWithCount(MenuRead):

    submenus_count: int | None = 0
    dishes_count: int | None = 0

    def get_counts(self):
        self.submenus_count = len(self.submenus)
        self.dishes_count = sum(len(submenu.dishes) for submenu in self.submenus)



