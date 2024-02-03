import uuid

from sqlalchemy import UUID, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class Menu(Base):  # type: ignore
    __tablename__ = 'menus'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),
                                     default=uuid.uuid4,
                                     primary_key=True,
                                     unique=True)
    title: Mapped[String] = mapped_column(String(64), nullable=False)
    description: Mapped[String] = mapped_column(String(512), nullable=False)

    submenus: Mapped[list['SubMenu']] = relationship('SubMenu',
                                                     back_populates='menu',
                                                     cascade='all, delete')


class SubMenu(Base):  # type: ignore
    __tablename__ = 'submenus'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),
                                     default=uuid.uuid4,
                                     primary_key=True,
                                     unique=True)
    title: Mapped[String] = mapped_column(String(64), nullable=False)
    menu_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),
                                          ForeignKey('menus.id', ondelete='CASCADE'))
    description: Mapped[String] = mapped_column(String(512), nullable=True)

    menu: Mapped[Menu] = relationship(Menu, back_populates='submenus')
    dishes: Mapped[list['Dish']] = relationship('Dish', back_populates='submenu', cascade='all, delete')


class Dish(Base):  # type: ignore
    __tablename__ = 'dishes'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),
                                     default=uuid.uuid4,
                                     primary_key=True,
                                     unique=True)
    submenu_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),
                                             ForeignKey('submenus.id', ondelete='CASCADE'))
    title: Mapped[String] = mapped_column(String(64), nullable=False)
    description: Mapped[String] = mapped_column(String(512), nullable=True)
    price: Mapped[Float] = mapped_column(Float, nullable=False)

    submenu: Mapped[SubMenu] = relationship(SubMenu, back_populates='dishes')
