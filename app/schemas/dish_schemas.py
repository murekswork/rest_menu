from uuid import UUID

from pydantic import BaseModel

from .base_schemas import TunedModel


class DishRead(TunedModel):
    id: UUID
    title: str
    price: float | str
    description: str

    def round_price(self):
        self.price = ('%.2f' % float(self.price))
        return self


class DishCreate(BaseModel):
    title: str
    price: float
    description: str


class DishCreateWithSubmenuId(DishCreate):
    submenu_id: UUID


class DishIdOnly(BaseModel):
    id: UUID
