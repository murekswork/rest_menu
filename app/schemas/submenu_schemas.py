from uuid import UUID

from pydantic import BaseModel

from app.schemas.dish_schemas import DishRead

from app.schemas.base_schemas import TunedModel


class SubmenuCreate(BaseModel):
    title: str
    description: str = 'description'


class SubmenuCreateWithMenuId(SubmenuCreate):
    menu_id: UUID


class SubmenuRead(TunedModel):
    id: UUID | str
    title: str
    description: str = 'description'
    dishes_count: int = 0
    dishes: list[DishRead] = []

    def get_dishes_count(self):
        self.dishes_count = len(self.dishes)
        return self


class SubmenuIdOnly(BaseModel):
    submenu_id: UUID
