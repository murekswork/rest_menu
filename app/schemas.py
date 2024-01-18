from typing import List

from pydantic import BaseModel, EmailStr, field_validator


class TunedModel(BaseModel):

    class Config:
        from_attributes = True


class DishRead(TunedModel):
    title: str
    price: float


class DishCreate(BaseModel):
    title: str
    price: float
    submenu_id: int


class MenuCreate(BaseModel):
    title: str
    description: str



class MenuCreateRead(MenuCreate):
    menu_id: int

class MenuIdOnly(BaseModel):
    menu_id: int



class SubmenuCreate(BaseModel):

    menu_id: int
    title: str


class SubmenuRead(TunedModel):
    submenu_id: int
    title: str
    dishes: List[DishRead] | None = None

    def get_dishes_count(self):
        self.dishes_count = len(self.dishes)

class SubmenuIdOnly(BaseModel):
    submenu_id: int


class MenuRead(TunedModel):
    menu_id: int
    title: str
    submenus: List[SubmenuRead] | None = None


