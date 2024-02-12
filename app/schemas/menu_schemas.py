from uuid import UUID

from pydantic import BaseModel

from app.schemas.base_schemas import TunedModel
from app.schemas.submenu_schemas import SubmenuRead


class MenuReadCounts(TunedModel):
    id: UUID
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class MenuRead(TunedModel):
    id: UUID | str
    title: str
    description: str
    dishes_count: int = 0
    submenus_count: int = 0
    submenus: list[SubmenuRead] = []

    def get_counts(self) -> 'MenuRead':
        """
        This method get_counts calculates the number of submenus and dishes
        within a menu and updates the corresponding counts in the MenuRead
        object. The method returns the updated MenuRead object with the counts
        included.
        """
        self.submenus_count = len(self.submenus)
        self.dishes_count = sum(
            submenu.dishes_count for submenu in self.submenus)
        return self


class MenuListSchema(BaseModel):
    menus: list[MenuRead]


class MenuReadWithCount(MenuRead):
    submenus_count: int = 0
    dishes_count: int = 0


class MenuCreate(BaseModel):
    title: str
    description: str


class MenuCreateRead(MenuCreate):
    menu_id: UUID


class MenuIdOnly(BaseModel):
    menu_id: UUID
