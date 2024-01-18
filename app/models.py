# from typing import List
#
# from sqlalchemy.orm import declarative_base, mapped_column, relationship, Mapped
# from sqlalchemy import UUID, String, Boolean, ForeignKey, Float, Integer
#
# Base = declarative_base()
#
# class Menu(Base):
#     __tablename__ = 'menus'
#     menu_id: Mapped[Integer] = mapped_column(Integer, primary_key=True, unique=True)
#     name: Mapped[String] = mapped_column(String(64), nullable=False, unique=True)
#
#     submenus: Mapped[List['SubMenu']] = relationship(back_populates='menu')
#
# class SubMenu(Base):
#     __tablename__ = 'submenus'
#     submenu_id: Mapped[Integer] = mapped_column(Integer, primary_key=True, unique=True)
#     name: Mapped[String] = mapped_column(String(64), unique=True, nullable=False)
#
#     menu: Mapped[Menu] = relationship(back_populates='submenus')
#     dishes: Mapped[List['Dish']] = relationship(back_populates='submenu')
#
#
# class Dish(Base):
#     __tablename__ = 'dishes'
#     dish_id: Mapped[Integer] = mapped_column(Integer, primary_key=True, unique=True)
#     name: Mapped[String] = mapped_column(String(64), unique=True, nullable=False)
#     price: Mapped[Float] = mapped_column(Float, nullable=False)
#     submenu: Mapped[SubMenu] = relationship(back_populates='dishes')
