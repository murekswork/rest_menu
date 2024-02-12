import logging
from uuid import UUID

from pydantic import BaseModel

from app.schemas.base_schemas import TunedModel


class DishRead(TunedModel):
    id: UUID
    title: str
    description: str
    price: float | str

    def round_price(self) -> 'DishRead':
        self.price = ('%.2f' % float(self.price))
        return self

    async def check_sale(self, cache):
        """
        Function that checks for a sale discount in the cache
        service and updates the price of an item accordingly.
        """
        sale = await cache.check_sale(self.id)

        v = float(self.price)

        if sale is not None:
            logging.warning(f'Found sale for {self.title} is {sale}%')
            v -= (v * float(sale) / 100)
        self.price = ('%.2f' % v)

        return self


class DishCreate(BaseModel):
    title: str
    description: str
    price: float


class DishCreateWithSubmenuId(DishCreate):
    submenu_id: UUID


class DishIdOnly(BaseModel):
    id: UUID
