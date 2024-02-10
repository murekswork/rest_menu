import logging
from uuid import UUID

from pydantic import BaseModel

from .base_schemas import TunedModel


class DishRead(TunedModel):
    id: UUID
    title: str
    description: str
    price: float | str

    def round_price(self):
        self.price = ('%.2f' % float(self.price))
        return self

    async def check_sale(self, cache):
        sale = await cache.check_sale(self.id)

        v = float(self.price)

        if sale is not None:
            logging.warning(f'Sale for {self.title} is {v}')
            v -= (v * float(sale) / 100)

        self.price = ('%.2f' % v)
        logging.info(f'Price for {self.title} is {self.price}')
        return self


class DishCreate(BaseModel):
    title: str
    description: str
    price: float


class DishCreateWithSubmenuId(DishCreate):
    submenu_id: UUID


class DishIdOnly(BaseModel):
    id: UUID
