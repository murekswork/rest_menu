import uuid
from typing import List

from sqlalchemy import UUID, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base, mapped_column, relationship, Mapped

Base = declarative_base()


class Menu(Base):
    __tablename__ = 'menus'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    title: Mapped[String] = mapped_column(String(64), nullable=False)
    description: Mapped[String] = mapped_column(String(512), nullable=False)

    submenus: Mapped[List['SubMenu']] = relationship('SubMenu', back_populates='menu', cascade='all, delete')


class SubMenu(Base):
    __tablename__ = 'submenus'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    title: Mapped[String] = mapped_column(String(64), nullable=False)
    menu_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('menus.id', ondelete='CASCADE'))
    description: Mapped[String] = mapped_column(String(512), nullable=True)

    menu: Mapped[Menu] = relationship(Menu, back_populates='submenus')
    dishes: Mapped[List['Dish']] = relationship('Dish', back_populates='submenu', cascade='all, delete')


class Dish(Base):
    __tablename__ = 'dishes'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    submenu_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('submenus.id', ondelete='CASCADE'))
    title: Mapped[String] = mapped_column(String(64), nullable=False)
    description: Mapped[String] = mapped_column(String(512), nullable=True)
    price: Mapped[Float] = mapped_column(Float, nullable=False)

    submenu: Mapped[SubMenu] = relationship(SubMenu, back_populates='dishes')
